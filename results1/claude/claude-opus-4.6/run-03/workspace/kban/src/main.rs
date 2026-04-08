mod app;
mod storage;
mod ui;

use std::io;

use crossterm::{
    event::{self, Event, KeyCode, KeyEventKind, KeyModifiers},
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
    ExecutableCommand,
};
use ratatui::prelude::*;

use app::{App, Mode};

fn main() -> io::Result<()> {
    let board = storage::load_board();
    let mut app = App::new(board);

    enable_raw_mode()?;
    io::stdout().execute(EnterAlternateScreen)?;
    let mut terminal = Terminal::new(CrosstermBackend::new(io::stdout()))?;

    loop {
        terminal.draw(|frame| ui::draw(frame, &app))?;

        if let Event::Key(key) = event::read()? {
            if key.kind != KeyEventKind::Press {
                continue;
            }

            match app.mode {
                Mode::Normal => handle_normal(&mut app, key.code, key.modifiers),
                Mode::Adding | Mode::Editing => handle_input(&mut app, key.code),
                Mode::Confirm => handle_confirm(&mut app, key.code),
            }
        }

        if app.should_quit {
            break;
        }
    }

    storage::save_board(&app.board);
    disable_raw_mode()?;
    io::stdout().execute(LeaveAlternateScreen)?;
    Ok(())
}

fn handle_normal(app: &mut App, code: KeyCode, modifiers: KeyModifiers) {
    let shift = modifiers.contains(KeyModifiers::SHIFT);
    match code {
        KeyCode::Char('q') | KeyCode::Esc => app.should_quit = true,
        KeyCode::Char('h') | KeyCode::Left if !shift => app.move_left(),
        KeyCode::Char('l') | KeyCode::Right if !shift => app.move_right(),
        KeyCode::Char('k') | KeyCode::Up => app.move_up(),
        KeyCode::Char('j') | KeyCode::Down => app.move_down(),
        KeyCode::Char('a') => app.start_adding(),
        KeyCode::Char('e') => app.start_editing(),
        KeyCode::Char('d') => app.ask_delete(),
        KeyCode::Enter => app.move_task_right(),
        KeyCode::Backspace => app.move_task_left(),
        KeyCode::Char('H') | KeyCode::Left if shift => app.move_task_left(),
        KeyCode::Char('L') | KeyCode::Right if shift => app.move_task_right(),
        _ => {}
    }
}

fn handle_input(app: &mut App, code: KeyCode) {
    match code {
        KeyCode::Enter => app.confirm_input(),
        KeyCode::Esc => app.cancel_input(),
        KeyCode::Backspace => app.input_backspace(),
        KeyCode::Delete => app.input_delete(),
        KeyCode::Left => app.input_left(),
        KeyCode::Right => app.input_right(),
        KeyCode::Home => app.input_home(),
        KeyCode::End => app.input_end(),
        KeyCode::Char(c) => app.input_char(c),
        _ => {}
    }
}

fn handle_confirm(app: &mut App, code: KeyCode) {
    match code {
        KeyCode::Char('y') | KeyCode::Char('Y') => app.confirm_delete(),
        KeyCode::Char('n') | KeyCode::Char('N') | KeyCode::Esc => app.cancel_input(),
        _ => {}
    }
}
