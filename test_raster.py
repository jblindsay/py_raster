import os, math
from raster import Raster, Array2D

def testRaster():
    print("Testing Raster:")

    print('Reading data...')
    test_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'test_data' + os.path.sep
    test_file = 'test.dep'
    raster = Raster.from_file(test_dir + test_file)
    new_raster = Raster.create_from_other(test_dir + 'delete_me.dep', raster)
    lower_limit = raster.minimum + 0.00*(raster.maximum - raster.minimum)
    upper_limit = raster.minimum + 0.9*(raster.maximum - raster.minimum)
    old_progress = 1
    for row in range(raster.rows):
        for col in range(raster.columns):
            z = raster[row, col]
            if z == raster.nodata:
                new_raster[row, col] = new_raster.nodata
            elif z < lower_limit:
                new_raster[row, col] = lower_limit
            elif z > upper_limit:
                new_raster[row, col] = upper_limit
            else:
                new_raster[row, col] = z

        progress = int(100.0 * (row+1) / raster.rows)
        if progress != old_progress:
            print('progress: {}%'.format(progress))
            old_progress = progress

    new_raster *= 2.0
    new_raster[100, 100] += 275.6

    print('Saving data...')
    new_raster.calculate_min_and_max()
    new_raster.display_minimum = new_raster.minimum + 0.1*(new_raster.maximum - new_raster.minimum)
    new_raster.display_maximum = new_raster.minimum + 0.8*(new_raster.maximum - new_raster.minimum)
    new_raster.write()

def testArray2D():
    print("Testing Array2D:")
    rows = 100
    columns = 200
    nodata = -999.0
    a2d = Array2D.create(rows, columns, nodata=nodata, initial_value=0.0)
    assert a2d.rows == rows
    assert a2d.columns == columns

    assert a2d[0, 0] == 0.0
    assert a2d[-10, -10] == nodata
    assert a2d[rows+1, columns+1] == nodata

    # set some values
    a2d[50, 50] = 1.0
    a2d[1, 1] = 100.0

    assert a2d[50, 50] == 1.0
    assert a2d[1, 1] == 100.0

    # test increment and decrement operators
    a2d[50, 50] += 1.0
    assert a2d[50, 50] == 2.0

    a2d[50, 50] -= 1.0
    assert a2d[50, 50] == 1.0

    # loop through each grid cell and sum the pixel values
    total = 0.0
    old_progress = -1
    for row in range(a2d.rows):
        for col in range(a2d.columns):
            z = a2d[row, col]
            if z != a2d.nodata:
                total += z

        progress = int(100.0 * (row+1) / a2d.rows)
        if progress != old_progress:
            print('progress: {}%'.format(progress))
            old_progress = progress

    assert total == 101.0
    print("Done!")

def filter():
    test_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'test_data' + os.path.sep
    test_file = test_dir + 'test.dep'
    output_file = test_dir + 'delete_me.dep'

    print('Reading data...')
    raster = Raster.from_file(test_file)

    output = Raster.create_from_other(output_file, raster)

    filter_size = 7
    mid_point = int(filter_size / 2.0)
    dx = []
    dy = []
    for r in range(filter_size):
        for c in range(filter_size):
            dx.append(c - mid_point)
            dy.append(r - mid_point)

    num_neighbours = len(dx)
    threshold = 10.0

    values = [0.0]*num_neighbours
    w = [0.0]*num_neighbours

    old_progress = 1
    for row in range(raster.rows):
        for col in range(raster.columns):
            z = raster[row, col]
            if z != raster.nodata:
                sum_w = 0.0
                for n in range(num_neighbours):
                    xn = col + dx[n]
                    yn = row + dy[n]
                    zn = raster[yn, xn]
                    if zn != raster.nodata:
                        values[n] = zn
                        diff = math.fabs(zn - z)
                        if diff < threshold:
                            w[n] = 1.0 - diff / threshold
                            sum_w += w[n]
                        else:
                            values[n] = 0.0
                            w[n] = 0.0
                    else:
                        values[n] = 0.0
                        w[n] = 0.0

                if sum_w > 0.0:
                    z = 0.0
                    for n in range(num_neighbours):
                        z += values[n] * w[n] / sum_w

                output[row, col] = z


        progress = int(100.0 * (row+1) / raster.rows)
        if progress != old_progress:
            print('progress: {}%'.format(progress))
            old_progress = progress

    print('Saving data...')
    output.write()

if __name__ == '__main__':
    testRaster()
    testArray2D()
    filter()
