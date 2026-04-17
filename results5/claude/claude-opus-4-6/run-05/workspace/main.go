package main

import (
	"os"
	"time"

	"github.com/gdamore/tcell/v2"
)

func main() {
	s, err := tcell.NewScreen()
	if err != nil {
		os.Exit(1)
	}
	if err := s.Init(); err != nil {
		os.Exit(1)
	}
	defer s.Fini()

	w, h := s.Size()
	gridW := (w - 2) / 2
	gridH := h - 3
	if gridW < 20 {
		gridW = 20
	}
	if gridH < 20 {
		gridH = 20
	}

	grid := NewGrid(gridW, gridH)
	patternIdx := 2
	grid.LoadPattern(Patterns[patternIdx])

	gen := 0
	speed := 5
	paused := false

	speeds := []time.Duration{
		500 * time.Millisecond,
		300 * time.Millisecond,
		200 * time.Millisecond,
		100 * time.Millisecond,
		70 * time.Millisecond,
		50 * time.Millisecond,
		30 * time.Millisecond,
		20 * time.Millisecond,
		10 * time.Millisecond,
		5 * time.Millisecond,
	}

	eventCh := make(chan tcell.Event)
	go func() {
		for {
			eventCh <- s.PollEvent()
		}
	}()

	ticker := time.NewTicker(speeds[speed])
	defer ticker.Stop()

	Draw(s, grid, gen, speed+1, Patterns[patternIdx].Name, paused)

	for {
		select {
		case ev := <-eventCh:
			switch e := ev.(type) {
			case *tcell.EventKey:
				quit := false
				switch {
				case e.Key() == tcell.KeyRune && e.Rune() == 'q':
					quit = true
				case e.Key() == tcell.KeyEscape || e.Key() == tcell.KeyCtrlC:
					quit = true
				case e.Key() == tcell.KeyRune && e.Rune() == ' ':
					paused = !paused
				case e.Key() == tcell.KeyRune && e.Rune() == 'n':
					grid.Tick()
					gen++
				case e.Key() == tcell.KeyRune && (e.Rune() == '+' || e.Rune() == '='):
					if speed < len(speeds)-1 {
						speed++
						ticker.Reset(speeds[speed])
					}
				case e.Key() == tcell.KeyRune && (e.Rune() == '-' || e.Rune() == '_'):
					if speed > 0 {
						speed--
						ticker.Reset(speeds[speed])
					}
				case e.Key() == tcell.KeyRune && e.Rune() == 'r':
					grid.LoadPattern(Patterns[patternIdx])
					gen = 0
				case e.Key() == tcell.KeyRune && e.Rune() >= '1' && e.Rune() <= '5':
					patternIdx = int(e.Rune()-'1') % len(Patterns)
					grid.LoadPattern(Patterns[patternIdx])
					gen = 0
				}
				if quit {
					return
				}
				Draw(s, grid, gen, speed+1, Patterns[patternIdx].Name, paused)
			case *tcell.EventResize:
				s.Sync()
				Draw(s, grid, gen, speed+1, Patterns[patternIdx].Name, paused)
			}
		case <-ticker.C:
			if !paused {
				grid.Tick()
				gen++
				Draw(s, grid, gen, speed+1, Patterns[patternIdx].Name, paused)
			}
		}
	}
}
