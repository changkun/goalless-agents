use std::fs;
use std::path::PathBuf;

use crate::app::Board;

fn data_path() -> PathBuf {
    let dir = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
    dir.join(".kban.json")
}

pub fn load_board() -> Board {
    let path = data_path();
    if path.exists() {
        let data = fs::read_to_string(&path).unwrap_or_default();
        serde_json::from_str(&data).unwrap_or_default()
    } else {
        Board::default()
    }
}

pub fn save_board(board: &Board) {
    let path = data_path();
    if let Ok(data) = serde_json::to_string_pretty(board) {
        let _ = fs::write(path, data);
    }
}
