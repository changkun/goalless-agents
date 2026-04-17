package main

import (
	"fmt"

	"github.com/gdamore/tcell/v2"
)

func ageColor(age uint8) tcell.Color {
	switch {
	case age == 1:
		return tcell.NewRGBColor(0, 255, 0)
	case age <= 3:
		return tcell.NewRGBColor(0, 200, 0)
	case age <= 6:
		return tcell.NewRGBColor(180, 200, 0)
	case age <= 10:
		return tcell.NewRGBColor(255, 100, 0)
	case age <= 20:
		return tcell.NewRGBColor(200, 30, 0)
	default:
		return tcell.NewRGBColor(120, 0, 0)
	}
}

func Draw(s tcell.Screen, g *Grid, gen int, speed int, patternName string, paused bool) {
	s.Clear()
	w, h := s.Size()

	gridW := g.Width
	gridH := g.Height
	ox := (w - gridW*2) / 2
	oy := (h - 1 - gridH) / 2
	if ox < 0 {
		ox = 0
	}
	if oy < 0 {
		oy = 0
	}

	for y := 0; y < gridH && oy+y < h-1; y++ {
		for x := 0; x < gridW && ox+x*2+1 < w; x++ {
			age := g.Get(x, y)
			if age > 0 {
				style := tcell.StyleDefault.Foreground(ageColor(age))
				s.SetContent(ox+x*2, oy+y, '█', nil, style)
				s.SetContent(ox+x*2+1, oy+y, '█', nil, style)
			}
		}
	}

	status := fmt.Sprintf(" Gen: %d │ Pop: %d │ Speed: %d │ Pattern: %s ",
		gen, g.Population(), speed, patternName)
	if paused {
		status += "│ PAUSED "
	}
	controls := " [Space] Pause  [N] Step  [+/-] Speed  [1-5] Pattern  [R] Reset  [Q] Quit "

	statusStyle := tcell.StyleDefault.
		Background(tcell.NewRGBColor(30, 30, 50)).
		Foreground(tcell.NewRGBColor(150, 200, 255))

	for i, ch := range status {
		if i < w {
			s.SetContent(i, h-2, ch, nil, statusStyle)
		}
	}
	for i := len(status); i < w; i++ {
		s.SetContent(i, h-2, ' ', nil, statusStyle)
	}

	controlStyle := tcell.StyleDefault.
		Background(tcell.NewRGBColor(20, 20, 35)).
		Foreground(tcell.NewRGBColor(100, 150, 200))

	for i, ch := range controls {
		if i < w {
			s.SetContent(i, h-1, ch, nil, controlStyle)
		}
	}
	for i := len(controls); i < w; i++ {
		s.SetContent(i, h-1, ' ', nil, controlStyle)
	}

	s.Show()
}
