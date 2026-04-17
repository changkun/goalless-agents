package main

type Grid struct {
	Width, Height int
	Cells         []uint8
}

func NewGrid(w, h int) *Grid {
	return &Grid{
		Width:  w,
		Height: h,
		Cells:  make([]uint8, w*h),
	}
}

func (g *Grid) idx(x, y int) int {
	x = ((x % g.Width) + g.Width) % g.Width
	y = ((y % g.Height) + g.Height) % g.Height
	return y*g.Width + x
}

func (g *Grid) Get(x, y int) uint8 {
	return g.Cells[g.idx(x, y)]
}

func (g *Grid) Set(x, y int, val uint8) {
	g.Cells[g.idx(x, y)] = val
}

func (g *Grid) Neighbors(x, y int) int {
	count := 0
	for dy := -1; dy <= 1; dy++ {
		for dx := -1; dx <= 1; dx++ {
			if dx == 0 && dy == 0 {
				continue
			}
			if g.Get(x+dx, y+dy) > 0 {
				count++
			}
		}
	}
	return count
}

func (g *Grid) Tick() {
	next := make([]uint8, len(g.Cells))
	for y := 0; y < g.Height; y++ {
		for x := 0; x < g.Width; x++ {
			n := g.Neighbors(x, y)
			alive := g.Get(x, y) > 0
			if alive && (n == 2 || n == 3) {
				age := g.Get(x, y)
				if age < 255 {
					age++
				}
				next[g.idx(x, y)] = age
			} else if !alive && n == 3 {
				next[g.idx(x, y)] = 1
			}
		}
	}
	g.Cells = next
}

func (g *Grid) Clear() {
	for i := range g.Cells {
		g.Cells[i] = 0
	}
}

func (g *Grid) LoadPattern(p Pattern) {
	g.Clear()
	cx, cy := g.Width/2, g.Height/2
	for _, c := range p.Cells {
		g.Set(cx+c[0], cy+c[1], 1)
	}
}

func (g *Grid) Population() int {
	count := 0
	for _, c := range g.Cells {
		if c > 0 {
			count++
		}
	}
	return count
}
