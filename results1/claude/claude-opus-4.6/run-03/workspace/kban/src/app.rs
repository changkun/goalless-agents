use chrono::Local;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub title: String,
    pub created_at: String,
}

impl Task {
    pub fn new(title: String) -> Self {
        Self {
            title,
            created_at: Local::now().format("%Y-%m-%d %H:%M").to_string(),
        }
    }
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct Board {
    pub todo: Vec<Task>,
    pub in_progress: Vec<Task>,
    pub done: Vec<Task>,
}

impl Board {
    pub fn column(&self, col: usize) -> &Vec<Task> {
        match col {
            0 => &self.todo,
            1 => &self.in_progress,
            _ => &self.done,
        }
    }

    pub fn column_mut(&mut self, col: usize) -> &mut Vec<Task> {
        match col {
            0 => &mut self.todo,
            1 => &mut self.in_progress,
            _ => &mut self.done,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Mode {
    Normal,
    Adding,
    Editing,
    Confirm,
}

pub struct App {
    pub board: Board,
    pub current_col: usize,
    pub selected: [usize; 3],
    pub mode: Mode,
    pub input: String,
    pub cursor_pos: usize,
    pub should_quit: bool,
}

impl App {
    pub fn new(board: Board) -> Self {
        Self {
            board,
            current_col: 0,
            selected: [0; 3],
            mode: Mode::Normal,
            input: String::new(),
            cursor_pos: 0,
            should_quit: false,
        }
    }

    pub fn current_selected(&self) -> usize {
        self.selected[self.current_col]
    }

    fn clamp_selected(&mut self) {
        let len = self.board.column(self.current_col).len();
        if len == 0 {
            self.selected[self.current_col] = 0;
        } else if self.selected[self.current_col] >= len {
            self.selected[self.current_col] = len - 1;
        }
    }

    pub fn move_left(&mut self) {
        if self.current_col > 0 {
            self.current_col -= 1;
            self.clamp_selected();
        }
    }

    pub fn move_right(&mut self) {
        if self.current_col < 2 {
            self.current_col += 1;
            self.clamp_selected();
        }
    }

    pub fn move_up(&mut self) {
        if self.selected[self.current_col] > 0 {
            self.selected[self.current_col] -= 1;
        }
    }

    pub fn move_down(&mut self) {
        let len = self.board.column(self.current_col).len();
        if len > 0 && self.selected[self.current_col] < len - 1 {
            self.selected[self.current_col] += 1;
        }
    }

    pub fn start_adding(&mut self) {
        self.mode = Mode::Adding;
        self.input.clear();
        self.cursor_pos = 0;
    }

    pub fn start_editing(&mut self) {
        let col = self.board.column(self.current_col);
        if col.is_empty() {
            return;
        }
        let idx = self.current_selected();
        self.input = col[idx].title.clone();
        self.cursor_pos = self.input.len();
        self.mode = Mode::Editing;
    }

    pub fn confirm_input(&mut self) {
        let text = self.input.trim().to_string();
        if text.is_empty() {
            self.mode = Mode::Normal;
            return;
        }

        match self.mode {
            Mode::Adding => {
                let task = Task::new(text);
                self.board.column_mut(self.current_col).push(task);
                let len = self.board.column(self.current_col).len();
                self.selected[self.current_col] = len - 1;
            }
            Mode::Editing => {
                let idx = self.current_selected();
                self.board.column_mut(self.current_col)[idx].title = text;
            }
            _ => {}
        }
        self.mode = Mode::Normal;
        self.input.clear();
    }

    pub fn cancel_input(&mut self) {
        self.mode = Mode::Normal;
        self.input.clear();
    }

    pub fn ask_delete(&mut self) {
        if !self.board.column(self.current_col).is_empty() {
            self.mode = Mode::Confirm;
        }
    }

    pub fn confirm_delete(&mut self) {
        let idx = self.current_selected();
        let col = self.board.column_mut(self.current_col);
        if idx < col.len() {
            col.remove(idx);
        }
        self.clamp_selected();
        self.mode = Mode::Normal;
    }

    pub fn move_task_right(&mut self) {
        if self.current_col >= 2 {
            return;
        }
        let col = self.board.column(self.current_col);
        if col.is_empty() {
            return;
        }
        let idx = self.current_selected();
        let task = self.board.column_mut(self.current_col).remove(idx);
        self.board.column_mut(self.current_col + 1).push(task);
        self.clamp_selected();
    }

    pub fn move_task_left(&mut self) {
        if self.current_col == 0 {
            return;
        }
        let col = self.board.column(self.current_col);
        if col.is_empty() {
            return;
        }
        let idx = self.current_selected();
        let task = self.board.column_mut(self.current_col).remove(idx);
        self.board.column_mut(self.current_col - 1).push(task);
        self.clamp_selected();
    }

    pub fn input_char(&mut self, c: char) {
        self.input.insert(self.cursor_pos, c);
        self.cursor_pos += 1;
    }

    pub fn input_backspace(&mut self) {
        if self.cursor_pos > 0 {
            self.cursor_pos -= 1;
            self.input.remove(self.cursor_pos);
        }
    }

    pub fn input_delete(&mut self) {
        if self.cursor_pos < self.input.len() {
            self.input.remove(self.cursor_pos);
        }
    }

    pub fn input_left(&mut self) {
        if self.cursor_pos > 0 {
            self.cursor_pos -= 1;
        }
    }

    pub fn input_right(&mut self) {
        if self.cursor_pos < self.input.len() {
            self.cursor_pos += 1;
        }
    }

    pub fn input_home(&mut self) {
        self.cursor_pos = 0;
    }

    pub fn input_end(&mut self) {
        self.cursor_pos = self.input.len();
    }
}
