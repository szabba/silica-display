int cube = 0;

for (int i = 0; i < W; i++) {
    for (int j = 0; j < H; j++) {
        for (int k = 0; k < D; k++) {

            int pos = i * H * D + j * D + k;

            if (grid[pos]) {

                for (int side = 0; side < SQUARES_PER_CUBE; side++) {

                    int side_ix = cube * SQUARES_PER_CUBE + side;

                    nonoverlap_mask[side_ix] =
                        overlaps_grid[side * W * H * D + pos];
                }

				cube++;
            }
        }
    }
}
