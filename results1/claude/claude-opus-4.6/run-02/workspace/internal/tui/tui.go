package tui

import (
	"fmt"
	"strings"

	"github.com/user/kb/internal/model"
	"github.com/user/kb/internal/store"

	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/key"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

var (
	columnStyle = lipgloss.NewStyle().
			Padding(1, 2).
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("62"))

	activeColumnStyle = lipgloss.NewStyle().
				Padding(1, 2).
				Border(lipgloss.RoundedBorder()).
				BorderForeground(lipgloss.Color("205"))

	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("205")).
			MarginBottom(1)

	taskStyle = lipgloss.NewStyle().
			PaddingLeft(1)

	selectedTaskStyle = lipgloss.NewStyle().
				PaddingLeft(1).
				Bold(true).
				Foreground(lipgloss.Color("229")).
				Background(lipgloss.Color("62"))

	priorityHighStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("196"))
	priorityMedStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color("214"))
	priorityLowStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color("245"))
	tagStyle            = lipgloss.NewStyle().Foreground(lipgloss.Color("39"))
	doneTaskStyle       = lipgloss.NewStyle().PaddingLeft(1).Foreground(lipgloss.Color("242")).Strikethrough(true)
	headerStyle         = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("99")).MarginBottom(1)
)

type keyMap struct {
	Left    key.Binding
	Right   key.Binding
	Up      key.Binding
	Down    key.Binding
	MoveL   key.Binding
	MoveR   key.Binding
	Delete  key.Binding
	Quit    key.Binding
	Help    key.Binding
	PriUp   key.Binding
	PriDown key.Binding
}

var keys = keyMap{
	Left:    key.NewBinding(key.WithKeys("h", "left"), key.WithHelp("h/←", "column left")),
	Right:   key.NewBinding(key.WithKeys("l", "right"), key.WithHelp("l/→", "column right")),
	Up:      key.NewBinding(key.WithKeys("k", "up"), key.WithHelp("k/↑", "task up")),
	Down:    key.NewBinding(key.WithKeys("j", "down"), key.WithHelp("j/↓", "task down")),
	MoveL:   key.NewBinding(key.WithKeys("H", "shift+left"), key.WithHelp("H", "move task left")),
	MoveR:   key.NewBinding(key.WithKeys("L", "shift+right"), key.WithHelp("L", "move task right")),
	Delete:  key.NewBinding(key.WithKeys("d", "delete"), key.WithHelp("d", "delete task")),
	PriUp:   key.NewBinding(key.WithKeys("+"), key.WithHelp("+", "priority up")),
	PriDown: key.NewBinding(key.WithKeys("-"), key.WithHelp("-", "priority down")),
	Quit:    key.NewBinding(key.WithKeys("q", "ctrl+c"), key.WithHelp("q", "quit")),
	Help:    key.NewBinding(key.WithKeys("?"), key.WithHelp("?", "help")),
}

func (k keyMap) ShortHelp() []key.Binding {
	return []key.Binding{k.Left, k.Right, k.Up, k.Down, k.MoveL, k.MoveR, k.Delete, k.Quit, k.Help}
}

func (k keyMap) FullHelp() [][]key.Binding {
	return [][]key.Binding{
		{k.Left, k.Right, k.Up, k.Down},
		{k.MoveL, k.MoveR, k.Delete, k.PriUp, k.PriDown},
		{k.Quit, k.Help},
	}
}

type Model struct {
	board     *model.Board
	path      string
	colIdx    int
	taskIdx   []int // cursor per column
	width     int
	height    int
	help      help.Model
	showHelp  bool
}

func New(board *model.Board, path string) Model {
	return Model{
		board:   board,
		path:    path,
		taskIdx: make([]int, len(model.Columns)),
		help:    help.New(),
	}
}

func (m Model) Init() tea.Cmd {
	return nil
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.help.Width = msg.Width
		return m, nil

	case tea.KeyMsg:
		switch {
		case key.Matches(msg, keys.Quit):
			return m, tea.Quit

		case key.Matches(msg, keys.Help):
			m.showHelp = !m.showHelp
			return m, nil

		case key.Matches(msg, keys.Left):
			if m.colIdx > 0 {
				m.colIdx--
			}

		case key.Matches(msg, keys.Right):
			if m.colIdx < len(model.Columns)-1 {
				m.colIdx++
			}

		case key.Matches(msg, keys.Up):
			tasks := m.board.TasksByColumn(model.Columns[m.colIdx])
			if m.taskIdx[m.colIdx] > 0 && len(tasks) > 0 {
				m.taskIdx[m.colIdx]--
			}

		case key.Matches(msg, keys.Down):
			tasks := m.board.TasksByColumn(model.Columns[m.colIdx])
			if m.taskIdx[m.colIdx] < len(tasks)-1 {
				m.taskIdx[m.colIdx]++
			}

		case key.Matches(msg, keys.MoveR):
			m.moveTask(1)

		case key.Matches(msg, keys.MoveL):
			m.moveTask(-1)

		case key.Matches(msg, keys.Delete):
			m.deleteSelected()

		case key.Matches(msg, keys.PriUp):
			if t := m.selectedTask(); t != nil && t.Priority < model.PriorityHigh {
				t.Priority++
				m.save()
			}

		case key.Matches(msg, keys.PriDown):
			if t := m.selectedTask(); t != nil && t.Priority > model.PriorityLow {
				t.Priority--
				m.save()
			}
		}
	}
	return m, nil
}

func (m *Model) selectedTask() *model.Task {
	col := model.Columns[m.colIdx]
	tasks := m.board.TasksByColumn(col)
	idx := m.taskIdx[m.colIdx]
	if idx >= len(tasks) || len(tasks) == 0 {
		return nil
	}
	return m.board.FindByID(tasks[idx].ID)
}

func (m *Model) moveTask(dir int) {
	col := model.Columns[m.colIdx]
	tasks := m.board.TasksByColumn(col)
	idx := m.taskIdx[m.colIdx]
	if idx >= len(tasks) || len(tasks) == 0 {
		return
	}
	newColIdx := m.colIdx + dir
	if newColIdx < 0 || newColIdx >= len(model.Columns) {
		return
	}
	task := tasks[idx]
	m.board.Move(task.ID, model.Columns[newColIdx])
	// adjust cursor
	if m.taskIdx[m.colIdx] >= len(m.board.TasksByColumn(col))-1 && m.taskIdx[m.colIdx] > 0 {
		m.taskIdx[m.colIdx]--
	}
	m.save()
}

func (m *Model) deleteSelected() {
	col := model.Columns[m.colIdx]
	tasks := m.board.TasksByColumn(col)
	idx := m.taskIdx[m.colIdx]
	if idx >= len(tasks) || len(tasks) == 0 {
		return
	}
	m.board.Delete(tasks[idx].ID)
	remaining := m.board.TasksByColumn(col)
	if m.taskIdx[m.colIdx] >= len(remaining) && m.taskIdx[m.colIdx] > 0 {
		m.taskIdx[m.colIdx]--
	}
	m.save()
}

func (m *Model) save() {
	_ = store.Save(m.path, m.board)
}

func (m Model) View() string {
	if m.width == 0 {
		return "Loading..."
	}

	colWidth := (m.width - 8) / len(model.Columns)
	if colWidth < 20 {
		colWidth = 20
	}

	header := headerStyle.Render(fmt.Sprintf("  kb: %s", m.board.Name))

	var cols []string
	for i, col := range model.Columns {
		tasks := m.board.TasksByColumn(col)
		label := model.ColumnLabel(col)
		title := titleStyle.Render(fmt.Sprintf("%s (%d)", label, len(tasks)))

		var lines []string
		lines = append(lines, title)

		for j, t := range tasks {
			line := m.renderTask(t, i == m.colIdx && j == m.taskIdx[i])
			lines = append(lines, line)
		}
		if len(tasks) == 0 {
			lines = append(lines, lipgloss.NewStyle().Foreground(lipgloss.Color("242")).Render("  (empty)"))
		}

		content := strings.Join(lines, "\n")
		style := columnStyle
		if i == m.colIdx {
			style = activeColumnStyle
		}
		cols = append(cols, style.Width(colWidth).Render(content))
	}

	board := lipgloss.JoinHorizontal(lipgloss.Top, cols...)

	var helpView string
	if m.showHelp {
		helpView = m.help.FullHelpView(keys.FullHelp())
	} else {
		helpView = m.help.ShortHelpView(keys.ShortHelp())
	}

	return header + "\n\n" + board + "\n\n" + helpView
}

func (m Model) renderTask(t model.Task, selected bool) string {
	var priIcon string
	switch t.Priority {
	case model.PriorityHigh:
		priIcon = priorityHighStyle.Render("●")
	case model.PriorityMedium:
		priIcon = priorityMedStyle.Render("●")
	default:
		priIcon = priorityLowStyle.Render("○")
	}

	title := fmt.Sprintf("%s #%d %s", priIcon, t.ID, t.Title)

	if len(t.Tags) > 0 {
		tags := tagStyle.Render("[" + strings.Join(t.Tags, ",") + "]")
		title += " " + tags
	}

	if t.Column == model.Done {
		return doneTaskStyle.Render(title)
	}

	if selected {
		return selectedTaskStyle.Render(title)
	}
	return taskStyle.Render(title)
}

func Run(board *model.Board, path string) error {
	m := New(board, path)
	p := tea.NewProgram(m, tea.WithAltScreen())
	_, err := p.Run()
	return err
}
