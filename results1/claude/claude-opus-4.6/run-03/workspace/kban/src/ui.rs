use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Clear, List, ListItem, Paragraph},
    Frame,
};

use crate::app::{App, Mode};

const COL_NAMES: [&str; 3] = ["Todo", "In Progress", "Done"];
const COL_COLORS: [Color; 3] = [Color::Cyan, Color::Yellow, Color::Green];

pub fn draw(frame: &mut Frame, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),  // title
            Constraint::Min(5),    // board
            Constraint::Length(3), // help bar
        ])
        .split(frame.area());

    draw_title(frame, chunks[0]);
    draw_board(frame, app, chunks[1]);
    draw_help(frame, app, chunks[2]);

    if app.mode == Mode::Adding || app.mode == Mode::Editing {
        draw_input(frame, app);
    }

    if app.mode == Mode::Confirm {
        draw_confirm(frame, app);
    }
}

fn draw_title(frame: &mut Frame, area: Rect) {
    let title = Paragraph::new(Line::from(vec![
        Span::styled(" kban ", Style::default().fg(Color::White).add_modifier(Modifier::BOLD)),
        Span::styled("— terminal kanban", Style::default().fg(Color::DarkGray)),
    ]))
    .block(Block::default().borders(Borders::ALL).border_style(Style::default().fg(Color::DarkGray)));
    frame.render_widget(title, area);
}

fn draw_board(frame: &mut Frame, app: &App, area: Rect) {
    let columns = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(33),
            Constraint::Percentage(34),
            Constraint::Percentage(33),
        ])
        .split(area);

    for col in 0..3 {
        let tasks = app.board.column(col);
        let is_active = col == app.current_col;
        let color = COL_COLORS[col];

        let header = format!(" {} ({}) ", COL_NAMES[col], tasks.len());

        let border_style = if is_active {
            Style::default().fg(color)
        } else {
            Style::default().fg(Color::DarkGray)
        };

        let block = Block::default()
            .title(Span::styled(
                header,
                Style::default().fg(color).add_modifier(Modifier::BOLD),
            ))
            .borders(Borders::ALL)
            .border_style(border_style);

        let items: Vec<ListItem> = tasks
            .iter()
            .enumerate()
            .map(|(i, task)| {
                let selected = is_active && i == app.selected[col];
                let style = if selected {
                    Style::default()
                        .fg(Color::Black)
                        .bg(color)
                        .add_modifier(Modifier::BOLD)
                } else {
                    Style::default().fg(Color::White)
                };
                let prefix = if selected { " > " } else { "   " };
                ListItem::new(format!("{}{}", prefix, task.title)).style(style)
            })
            .collect();

        let list = List::new(items).block(block);
        frame.render_widget(list, columns[col]);
    }
}

fn draw_help(frame: &mut Frame, app: &App, area: Rect) {
    let help_text = match app.mode {
        Mode::Normal => {
            vec![
                Span::styled(" a", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
                Span::raw("dd "),
                Span::styled("e", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
                Span::raw("dit "),
                Span::styled("d", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw("elete "),
                Span::styled("h/l", Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD)),
                Span::raw(" columns "),
                Span::styled("j/k", Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD)),
                Span::raw(" tasks "),
                Span::styled("Enter", Style::default().fg(Color::Green).add_modifier(Modifier::BOLD)),
                Span::raw(" move→ "),
                Span::styled("Bksp", Style::default().fg(Color::Green).add_modifier(Modifier::BOLD)),
                Span::raw(" ←move "),
                Span::styled("q", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw("uit"),
            ]
        }
        Mode::Adding | Mode::Editing => {
            vec![
                Span::styled("Enter", Style::default().fg(Color::Green).add_modifier(Modifier::BOLD)),
                Span::raw(" confirm  "),
                Span::styled("Esc", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw(" cancel"),
            ]
        }
        Mode::Confirm => {
            vec![
                Span::styled("y", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)),
                Span::raw("es delete  "),
                Span::styled("n", Style::default().fg(Color::Green).add_modifier(Modifier::BOLD)),
                Span::raw("/Esc cancel"),
            ]
        }
    };

    let help = Paragraph::new(Line::from(help_text))
        .block(Block::default().borders(Borders::ALL).border_style(Style::default().fg(Color::DarkGray)));
    frame.render_widget(help, area);
}

fn draw_input(frame: &mut Frame, app: &App) {
    let area = frame.area();
    let popup = centered_rect(60, 3, area);

    let label = match app.mode {
        Mode::Adding => "New Task",
        Mode::Editing => "Edit Task",
        _ => "",
    };

    frame.render_widget(Clear, popup);
    let input = Paragraph::new(app.input.as_str())
        .block(
            Block::default()
                .title(Span::styled(
                    format!(" {} ", label),
                    Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD),
                ))
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Cyan)),
        )
        .style(Style::default().fg(Color::White));
    frame.render_widget(input, popup);

    // Set cursor position
    frame.set_cursor_position((
        popup.x + app.cursor_pos as u16 + 1,
        popup.y + 1,
    ));
}

fn draw_confirm(frame: &mut Frame, app: &App) {
    let area = frame.area();
    let popup = centered_rect(50, 3, area);

    let task_name = app
        .board
        .column(app.current_col)
        .get(app.current_selected())
        .map(|t| t.title.as_str())
        .unwrap_or("?");

    frame.render_widget(Clear, popup);
    let confirm = Paragraph::new(format!("Delete \"{}\"? (y/n)", task_name))
        .block(
            Block::default()
                .title(Span::styled(
                    " Confirm ",
                    Style::default().fg(Color::Red).add_modifier(Modifier::BOLD),
                ))
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Red)),
        )
        .style(Style::default().fg(Color::White));
    frame.render_widget(confirm, popup);
}

fn centered_rect(percent_x: u16, height: u16, area: Rect) -> Rect {
    let popup_layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length((area.height.saturating_sub(height)) / 2),
            Constraint::Length(height),
            Constraint::Min(0),
        ])
        .split(area);

    Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage((100 - percent_x) / 2),
            Constraint::Percentage(percent_x),
            Constraint::Percentage((100 - percent_x) / 2),
        ])
        .split(popup_layout[1])[1]
}
