package main

import (
	"flag"
	"log"
	"os"
	"strconv"
	"time"

	"math/rand"
)

func main() {
	p := flag.Int("p", 100, "number of papers")
	r := flag.Int("r", 100, "number of reviewers")
	f := flag.String("f", "matrix.txt", "output file name")
	flag.Parse()

	if *p < 1 || *r < 1 {
		return
	}
	matrix := genMatrix(*r, *p)

	file, err := os.Create(*f)
	if err != nil {
		log.Fatalf("failed to create file: %s", *f)
		return
	}
	defer file.Close()
	file.Write(intMatrix(matrix).ByteSlice())
}

type intMatrix [][]int

func (m intMatrix) String() string {
	return string(m.ByteSlice())
}

func (m intMatrix) ByteSlice() []byte {
	// Create a sufficient big slice to avoid
	// syscalls the great enemy of speed.
	bs := make([]byte, 0, len(m)*len(m[0])*3)
	for i := 0; i < len(m); i++ {
		for _, n := range m[i][:len(m[i])-1] {
			// Use the fast way:
			// We know that this number is in [0, 5]
			// so just add the number to byte '0'.
			bs = append(bs, byte('0'+n))
			bs = append(bs, ',')
		}
		// The last number can be bigger than 9 so we need
		// to user Itoa to convert it.
		bs = append(bs, strconv.Itoa(m[i][len(m[i])-1])...)
		bs = append(bs, '\n')
	}
	return bs
}

func doWork(matrix [][]int, done chan<- int, sReviewers, eReviewers, nPapers int) {
	totalOfReviews := 0
	random := rand.New(rand.NewSource(time.Now().UnixNano()))
	for i := sReviewers; i < eReviewers; i++ {
		matrix[i] = make([]int, nPapers+1)
		for j := 0; j < nPapers; j++ {
			matrix[i][j] = random.Intn(6)
		}
		matrix[i][nPapers] = random.Intn(nPapers) + 1
		totalOfReviews += matrix[i][nPapers]
	}
	done <- totalOfReviews
}

func genMatrix(nReviewers, nPapers int) [][]int {
	matrix := make([][]int, nReviewers)
	totalOfReviews := 0
	div := 8
	done := make(chan int)
	sReviewers := 0
	eReviewers := nReviewers / div

	for i := 0; i < div-1; i++ {
		go doWork(matrix, done, sReviewers, eReviewers, nPapers)
		sReviewers = eReviewers
		eReviewers += nReviewers / div
	}
	go doWork(matrix, done, sReviewers, nReviewers, nPapers)

	for i := 0; i < div; i++ {
		totalOfReviews += <-done
	}

	if totalOfReviews < nPapers {
		matrix[nReviewers-1][nPapers] += nPapers - totalOfReviews
	}
	return matrix
}
