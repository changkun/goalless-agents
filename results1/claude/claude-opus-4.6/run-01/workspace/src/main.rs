use clap::Parser;
use crossterm::{
    cursor,
    event::{self, Event, KeyCode, KeyEvent, KeyModifiers},
    execute, queue,
    style::{self, Color, SetBackgroundColor, SetForegroundColor},
    terminal::{self, ClearType},
};
use std::fs;
use std::io::{self, Write};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "hx", about = "Fast TUI hex viewer and editor")]
struct Cli {
    /// File to open
    file: PathBuf,

    /// Bytes per row (default: 16)
    #[arg(short = 'c', long = "columns", default_value = "16")]
    columns: usize,

    /// Read-only mode
    #[arg(short, long)]
    readonly: bool,
}

#[derive(Clone, Copy, PartialEq)]
enum Mode {
    Normal,
    Edit,
    Search,
    GoTo,
    Help,
}

#[derive(Clone, Copy, PartialEq)]
enum Nibble {
    High,
    Low,
}

struct App {
    data: Vec<u8>,
    original: Vec<u8>,
    path: PathBuf,
    columns: usize,
    readonly: bool,
    cursor: usize,
    scroll_offset: usize,
    mode: Mode,
    nibble: Nibble,
    input_buf: String,
    search_results: Vec<usize>,
    search_idx: usize,
    status_msg: String,
    modified: bool,
    rows: usize,
    cols: usize,
}

impl App {
    fn new(path: PathBuf, columns: usize, readonly: bool) -> io::Result<Self> {
        let data = if path.exists() {
            fs::read(&path)?
        } else {
            Vec::new()
        };
        let original = data.clone();
        let (cols, rows) = terminal::size()?;
        Ok(Self {
            data,
            original,
            path,
            columns,
            readonly,
            cursor: 0,
            scroll_offset: 0,
            mode: Mode::Normal,
            nibble: Nibble::High,
            input_buf: String::new(),
            search_results: Vec::new(),
            search_idx: 0,
            status_msg: String::new(),
            modified: false,
            rows: rows as usize,
            cols: cols as usize,
        })
    }

    fn visible_rows(&self) -> usize {
        self.rows.saturating_sub(3) // header + status + input line
    }

    fn total_rows(&self) -> usize {
        if self.data.is_empty() {
            0
        } else {
            (self.data.len() + self.columns - 1) / self.columns
        }
    }

    fn cursor_row(&self) -> usize {
        self.cursor / self.columns
    }

    fn cursor_col(&self) -> usize {
        self.cursor % self.columns
    }

    fn ensure_visible(&mut self) {
        let row = self.cursor_row();
        if row < self.scroll_offset {
            self.scroll_offset = row;
        }
        if row >= self.scroll_offset + self.visible_rows() {
            self.scroll_offset = row - self.visible_rows() + 1;
        }
    }

    fn run(&mut self) -> io::Result<()> {
        terminal::enable_raw_mode()?;
        let mut stdout = io::stdout();
        execute!(
            stdout,
            terminal::EnterAlternateScreen,
            cursor::Hide,
            event::EnableMouseCapture
        )?;

        let result = self.main_loop(&mut stdout);

        execute!(
            stdout,
            event::DisableMouseCapture,
            cursor::Show,
            terminal::LeaveAlternateScreen
        )?;
        terminal::disable_raw_mode()?;

        result
    }

    fn main_loop(&mut self, stdout: &mut io::Stdout) -> io::Result<()> {
        loop {
            self.render(stdout)?;
            match event::read()? {
                Event::Key(key) => match self.mode {
                    Mode::Normal => {
                        if self.handle_normal(key) {
                            break;
                        }
                    }
                    Mode::Edit => self.handle_edit(key),
                    Mode::Search => self.handle_search(key),
                    Mode::GoTo => self.handle_goto(key),
                    Mode::Help => self.handle_help(key),
                },
                Event::Resize(c, r) => {
                    self.cols = c as usize;
                    self.rows = r as usize;
                }
                _ => {}
            }
        }
        Ok(())
    }

    fn render(&self, stdout: &mut io::Stdout) -> io::Result<()> {
        queue!(stdout, terminal::Clear(ClearType::All), cursor::MoveTo(0, 0))?;

        // Header
        let title = format!(
            " hx — {} {}({} bytes)",
            self.path.display(),
            if self.modified { "[modified] " } else { "" },
            self.data.len()
        );
        queue!(
            stdout,
            SetBackgroundColor(Color::DarkBlue),
            SetForegroundColor(Color::White),
            style::Print(format!("{:<width$}", title, width = self.cols)),
            style::ResetColor
        )?;

        // Column header
        queue!(stdout, cursor::MoveTo(0, 1))?;
        queue!(
            stdout,
            SetForegroundColor(Color::DarkGrey),
            style::Print(format!("{:>10}  ", "Offset"))
        )?;
        for i in 0..self.columns {
            queue!(stdout, style::Print(format!("{:02X} ", i)))?;
        }
        queue!(stdout, style::Print(" │ ASCII"), style::ResetColor)?;

        // Data rows
        let vis = self.visible_rows();
        for row_idx in 0..vis {
            let data_row = self.scroll_offset + row_idx;
            let offset = data_row * self.columns;
            if offset >= self.data.len() {
                queue!(stdout, cursor::MoveTo(0, (row_idx + 2) as u16))?;
                queue!(stdout, style::Print(format!("{:width$}", "", width = self.cols)))?;
                continue;
            }

            queue!(stdout, cursor::MoveTo(0, (row_idx + 2) as u16))?;

            // Offset
            queue!(
                stdout,
                SetForegroundColor(Color::DarkYellow),
                style::Print(format!("0x{:08X}  ", offset)),
                style::ResetColor
            )?;

            // Hex bytes
            let end = (offset + self.columns).min(self.data.len());
            for i in offset..offset + self.columns {
                if i < end {
                    let byte = self.data[i];
                    let is_cursor = i == self.cursor;
                    let is_modified = i < self.data.len()
                        && (i >= self.original.len() || self.data[i] != self.original[i]);
                    let is_search_hit = self.search_results.contains(&i);

                    if is_cursor && (self.mode == Mode::Edit || self.mode == Mode::Normal) {
                        queue!(
                            stdout,
                            SetBackgroundColor(Color::White),
                            SetForegroundColor(Color::Black)
                        )?;
                    } else if is_search_hit {
                        queue!(
                            stdout,
                            SetBackgroundColor(Color::DarkYellow),
                            SetForegroundColor(Color::Black)
                        )?;
                    } else if is_modified {
                        queue!(stdout, SetForegroundColor(Color::Red))?;
                    }

                    queue!(stdout, style::Print(format!("{:02X}", byte)))?;
                    queue!(stdout, style::ResetColor)?;
                    queue!(stdout, style::Print(" "))?;
                } else {
                    queue!(stdout, style::Print("   "))?;
                }
            }

            // ASCII column
            queue!(stdout, style::Print(" │ "))?;
            for i in offset..end {
                let byte = self.data[i];
                let ch = if byte.is_ascii_graphic() || byte == b' ' {
                    byte as char
                } else {
                    '·'
                };
                let is_cursor = i == self.cursor;
                let is_modified = i >= self.original.len() || self.data[i] != self.original[i];

                if is_cursor {
                    queue!(
                        stdout,
                        SetBackgroundColor(Color::White),
                        SetForegroundColor(Color::Black),
                        style::Print(ch),
                        style::ResetColor
                    )?;
                } else if is_modified {
                    queue!(
                        stdout,
                        SetForegroundColor(Color::Red),
                        style::Print(ch),
                        style::ResetColor
                    )?;
                } else {
                    queue!(stdout, style::Print(ch))?;
                }
            }
        }

        // Status bar
        let status_y = (self.rows - 2) as u16;
        queue!(stdout, cursor::MoveTo(0, status_y))?;
        let mode_str = match self.mode {
            Mode::Normal => "NORMAL",
            Mode::Edit => "EDIT",
            Mode::Search => "SEARCH",
            Mode::GoTo => "GOTO",
            Mode::Help => "HELP",
        };
        let ro = if self.readonly { " [RO]" } else { "" };
        let pos = format!(
            "0x{:08X} ({}) | Row {}/{} | Col {}/{}",
            self.cursor,
            self.cursor,
            self.cursor_row() + 1,
            self.total_rows(),
            self.cursor_col() + 1,
            self.columns
        );
        let left = format!(" {} {}{}", mode_str, self.status_msg, ro);
        let padding = self.cols.saturating_sub(left.len() + pos.len() + 1);
        queue!(
            stdout,
            SetBackgroundColor(Color::DarkGreen),
            SetForegroundColor(Color::White),
            style::Print(format!(
                "{}{:>width$} ",
                left,
                pos,
                width = padding + pos.len()
            )),
            style::ResetColor
        )?;

        // Input/command line
        let cmd_y = (self.rows - 1) as u16;
        queue!(stdout, cursor::MoveTo(0, cmd_y))?;
        match self.mode {
            Mode::Search => {
                queue!(
                    stdout,
                    style::Print(format!("Search: {}_", self.input_buf))
                )?;
            }
            Mode::GoTo => {
                queue!(
                    stdout,
                    style::Print(format!("Go to offset: {}_", self.input_buf))
                )?;
            }
            _ => {
                queue!(
                    stdout,
                    SetForegroundColor(Color::DarkGrey),
                    style::Print("q:Quit  i:Edit  /:Search  g:GoTo  ?:Help  s:Save  u:Undo"),
                    style::ResetColor
                )?;
            }
        }

        // Help overlay
        if self.mode == Mode::Help {
            let help = [
                "                 hx — Hex Editor Help",
                "",
                "  Navigation",
                "    h/Left      Move left          l/Right    Move right",
                "    k/Up        Move up            j/Down     Move down",
                "    PageUp      Page up            PageDown   Page down",
                "    Home        Start of file      End        End of file",
                "",
                "  Commands",
                "    i/Enter     Enter edit mode    Esc        Back to normal",
                "    /           Search (hex or ASCII)",
                "    g           Go to offset (decimal or 0x hex)",
                "    n/N         Next/previous search result",
                "    s           Save file          u          Undo all changes",
                "    q           Quit               ?          Toggle help",
                "",
                "  Edit Mode",
                "    0-9, a-f    Type hex digits to modify bytes",
                "    Esc         Return to normal mode",
                "",
                "              Press Esc or ? to close",
            ];
            let box_w = 60;
            let box_h = help.len() + 2;
            let start_col = self.cols.saturating_sub(box_w) / 2;
            let start_row = self.rows.saturating_sub(box_h) / 2;

            for (i, line) in help.iter().enumerate() {
                queue!(
                    stdout,
                    cursor::MoveTo(start_col as u16, (start_row + i + 1) as u16),
                    SetBackgroundColor(Color::DarkBlue),
                    SetForegroundColor(Color::White),
                    style::Print(format!("{:<width$}", line, width = box_w)),
                    style::ResetColor
                )?;
            }
        }

        stdout.flush()
    }

    fn handle_normal(&mut self, key: KeyEvent) -> bool {
        self.status_msg.clear();
        match key.code {
            KeyCode::Char('q') | KeyCode::Esc => {
                if self.modified {
                    self.status_msg = "Unsaved changes! Press Q again or :wq".into();
                    // Simple: any q quits for now. A real app would track double-press.
                    return true;
                }
                return true;
            }
            KeyCode::Char('c') if key.modifiers.contains(KeyModifiers::CONTROL) => return true,

            // Navigation
            KeyCode::Left | KeyCode::Char('h') => self.move_cursor_left(),
            KeyCode::Right | KeyCode::Char('l') => self.move_cursor_right(),
            KeyCode::Up | KeyCode::Char('k') => self.move_cursor_up(),
            KeyCode::Down | KeyCode::Char('j') => self.move_cursor_down(),
            KeyCode::PageUp => self.page_up(),
            KeyCode::PageDown => self.page_down(),
            KeyCode::Home => {
                self.cursor = 0;
                self.ensure_visible();
            }
            KeyCode::End => {
                if !self.data.is_empty() {
                    self.cursor = self.data.len() - 1;
                    self.ensure_visible();
                }
            }

            // Modes
            KeyCode::Char('i') | KeyCode::Enter => {
                if !self.readonly {
                    self.mode = Mode::Edit;
                    self.nibble = Nibble::High;
                } else {
                    self.status_msg = "Read-only mode".into();
                }
            }
            KeyCode::Char('/') => {
                self.mode = Mode::Search;
                self.input_buf.clear();
            }
            KeyCode::Char('g') => {
                self.mode = Mode::GoTo;
                self.input_buf.clear();
            }
            KeyCode::Char('?') => {
                self.mode = Mode::Help;
            }
            KeyCode::Char('n') => self.next_search_result(),
            KeyCode::Char('N') => self.prev_search_result(),

            // Actions
            KeyCode::Char('s') => self.save(),
            KeyCode::Char('u') => self.undo(),

            _ => {}
        }
        false
    }

    fn handle_edit(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Esc => {
                self.mode = Mode::Normal;
            }
            KeyCode::Left => self.move_cursor_left(),
            KeyCode::Right => self.move_cursor_right(),
            KeyCode::Up => self.move_cursor_up(),
            KeyCode::Down => self.move_cursor_down(),
            KeyCode::Char(c) if c.is_ascii_hexdigit() => {
                if self.cursor < self.data.len() {
                    let val = c.to_digit(16).unwrap() as u8;
                    match self.nibble {
                        Nibble::High => {
                            self.data[self.cursor] = (val << 4) | (self.data[self.cursor] & 0x0F);
                            self.nibble = Nibble::Low;
                        }
                        Nibble::Low => {
                            self.data[self.cursor] = (self.data[self.cursor] & 0xF0) | val;
                            self.nibble = Nibble::High;
                            self.move_cursor_right();
                        }
                    }
                    self.modified = true;
                }
            }
            _ => {}
        }
    }

    fn handle_search(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Esc => {
                self.mode = Mode::Normal;
                self.input_buf.clear();
            }
            KeyCode::Enter => {
                self.execute_search();
                self.mode = Mode::Normal;
            }
            KeyCode::Backspace => {
                self.input_buf.pop();
            }
            KeyCode::Char(c) => {
                self.input_buf.push(c);
            }
            _ => {}
        }
    }

    fn handle_goto(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Esc => {
                self.mode = Mode::Normal;
                self.input_buf.clear();
            }
            KeyCode::Enter => {
                self.execute_goto();
                self.mode = Mode::Normal;
            }
            KeyCode::Backspace => {
                self.input_buf.pop();
            }
            KeyCode::Char(c) => {
                self.input_buf.push(c);
            }
            _ => {}
        }
    }

    fn handle_help(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Esc | KeyCode::Char('q') | KeyCode::Char('?') => {
                self.mode = Mode::Normal;
            }
            _ => {}
        }
    }

    fn move_cursor_left(&mut self) {
        if self.cursor > 0 {
            self.cursor -= 1;
            self.nibble = Nibble::High;
            self.ensure_visible();
        }
    }

    fn move_cursor_right(&mut self) {
        if self.cursor + 1 < self.data.len() {
            self.cursor += 1;
            self.nibble = Nibble::High;
            self.ensure_visible();
        }
    }

    fn move_cursor_up(&mut self) {
        if self.cursor >= self.columns {
            self.cursor -= self.columns;
            self.ensure_visible();
        }
    }

    fn move_cursor_down(&mut self) {
        if self.cursor + self.columns < self.data.len() {
            self.cursor += self.columns;
            self.ensure_visible();
        }
    }

    fn page_up(&mut self) {
        let jump = self.visible_rows() * self.columns;
        self.cursor = self.cursor.saturating_sub(jump);
        self.scroll_offset = self.scroll_offset.saturating_sub(self.visible_rows());
    }

    fn page_down(&mut self) {
        let jump = self.visible_rows() * self.columns;
        self.cursor = (self.cursor + jump).min(self.data.len().saturating_sub(1));
        self.ensure_visible();
    }

    fn execute_search(&mut self) {
        let query = self.input_buf.clone();
        self.search_results.clear();
        self.search_idx = 0;

        if query.is_empty() {
            return;
        }

        // Try hex pattern first (e.g., "FF 00 AB" or "ff00ab")
        let hex_clean: String = query.chars().filter(|c| c.is_ascii_hexdigit()).collect();
        if hex_clean.len() >= 2 && hex_clean.len() % 2 == 0 {
            let pattern: Vec<u8> = (0..hex_clean.len())
                .step_by(2)
                .filter_map(|i| u8::from_str_radix(&hex_clean[i..i + 2], 16).ok())
                .collect();

            if pattern.len() == hex_clean.len() / 2 {
                for i in 0..=self.data.len().saturating_sub(pattern.len()) {
                    if self.data[i..i + pattern.len()] == pattern[..] {
                        self.search_results.push(i);
                    }
                }
            }
        }

        // Also search as ASCII string
        if self.search_results.is_empty() {
            let pattern = query.as_bytes();
            for i in 0..=self.data.len().saturating_sub(pattern.len()) {
                if self.data[i..i + pattern.len()] == pattern[..] {
                    self.search_results.push(i);
                }
            }
        }

        if self.search_results.is_empty() {
            self.status_msg = format!("No matches for '{}'", query);
        } else {
            self.status_msg = format!("{} match(es)", self.search_results.len());
            self.cursor = self.search_results[0];
            self.ensure_visible();
        }
    }

    fn next_search_result(&mut self) {
        if !self.search_results.is_empty() {
            self.search_idx = (self.search_idx + 1) % self.search_results.len();
            self.cursor = self.search_results[self.search_idx];
            self.status_msg = format!(
                "Match {}/{}",
                self.search_idx + 1,
                self.search_results.len()
            );
            self.ensure_visible();
        }
    }

    fn prev_search_result(&mut self) {
        if !self.search_results.is_empty() {
            if self.search_idx == 0 {
                self.search_idx = self.search_results.len() - 1;
            } else {
                self.search_idx -= 1;
            }
            self.cursor = self.search_results[self.search_idx];
            self.status_msg = format!(
                "Match {}/{}",
                self.search_idx + 1,
                self.search_results.len()
            );
            self.ensure_visible();
        }
    }

    fn execute_goto(&mut self) {
        let input = self.input_buf.trim().to_string();
        let offset = if input.starts_with("0x") || input.starts_with("0X") {
            usize::from_str_radix(&input[2..], 16).ok()
        } else if input.ends_with('h') || input.ends_with('H') {
            usize::from_str_radix(&input[..input.len() - 1], 16).ok()
        } else {
            input.parse::<usize>().ok()
        };

        match offset {
            Some(off) if off < self.data.len() => {
                self.cursor = off;
                self.ensure_visible();
                self.status_msg = format!("Jumped to 0x{:08X}", off);
            }
            Some(off) => {
                self.status_msg = format!(
                    "Offset 0x{:X} out of range (max 0x{:X})",
                    off,
                    self.data.len().saturating_sub(1)
                );
            }
            None => {
                self.status_msg = format!("Invalid offset: '{}'", input);
            }
        }
    }

    fn save(&mut self) {
        if self.readonly {
            self.status_msg = "Read-only mode — cannot save".into();
            return;
        }
        match fs::write(&self.path, &self.data) {
            Ok(()) => {
                self.original = self.data.clone();
                self.modified = false;
                self.status_msg = format!("Saved {} bytes to {}", self.data.len(), self.path.display());
            }
            Err(e) => {
                self.status_msg = format!("Save failed: {}", e);
            }
        }
    }

    fn undo(&mut self) {
        self.data = self.original.clone();
        self.modified = false;
        self.status_msg = "Reverted to last saved state".into();
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let mut app = App::new(cli.file, cli.columns, cli.readonly)?;
    app.run()?;
    Ok(())
}
