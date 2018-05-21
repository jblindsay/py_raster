import os
import struct
import math


class Raster(object):

    @staticmethod
    def from_file(filename):
        r = Raster()
        if filename.lower().endswith('.dep'):
            r.header_filename = filename
            r.data_filename = filename.replace(
                '.dep', '.tas').replace('.DEP', '.tas')
        elif filename.lower().endswith('.tas'):
            r.header_filename = filename.replace(
                '.tas', '.dep').replace('.TAS', '.dep')
            r.data_filename = filename
        else:
            raise Exception("Unknown file extension")

        r.read()
        return r

    @staticmethod
    def create(filename, rows, columns, nodata):
        r = Raster()
        if filename.lower().endswith('.dep'):
            r.header_filename = filename
            r.data_filename = filename.replace(
                '.dep', '.tas').replace('.DEP', '.tas')
        elif filename.lower().endswith('.tas'):
            r.header_filename = filename.replace(
                '.tas', '.dep').replace('.TAS', '.dep')
            r.data_filename = filename
        else:
            raise Exception("Unknown file extension")

        r.rows = rows
        r.columns = columns
        r.nodata = nodata
        r._values = [nodata] * rows * columns
        return r

    @staticmethod
    def create_from_other(filename, other, data_type=None, nodata=None, initial_value=None):
        r = Raster()
        if filename.lower().endswith('.dep'):
            r.header_filename = filename
            r.data_filename = filename.replace(
                '.dep', '.tas').replace('.DEP', '.tas')
        elif filename.lower().endswith('.tas'):
            r.header_filename = filename.replace(
                '.tas', '.dep').replace('.TAS', '.dep')
            r.data_filename = filename
        else:
            raise Exception("Unknown file extension")

        if type(other) is str:
            other = Raster.from_file(other)

        if not type(other) is Raster:
            raise Exception("Parameter 'other' must be a Raster or file name.")

        # copy parameters unrelated to the data and metadata
        r.north = other.north
        r.south = other.south
        r.east = other.east
        r.west = other.west
        r.rows = other.rows
        r.columns = other.columns
        r.resolution_x = other.resolution_x
        r.resolution_y = other.resolution_y
        r.stacks = 1  # other.stacks
        if not nodata:
            r.nodata = other.nodata
        else:
            r.nodata = nodata
        r.data_scale = other.data_scale
        if not data_type:
            r.data_type = other.data_type
        else:
            r.data_type = data_type
        r.palette = other.palette
        r.palette_nonlinearity = 1.0  # other.palette_nonlinearity
        r.projection = other.projection
        r.z_units = other.z_units
        r.xy_units = other.xy_units
        r.byte_order = other.byte_order

        # the data will be unique to the new raster
        r.minimum = float("inf")
        r.maximum = float("-inf")
        r.display_minimum = float("inf")
        r.display_maximum = float("-inf")

        if initial_value is None:
            r._values = [r.nodata] * r.rows * r.columns
        else:
            r._values = [initial_value] * r.rows * r.columns

        # the metadata will also be unique
        r.metadata = []

        return r

    def __getitem__(self, pos):
        """Array indexing operator for Raster
        """
        row, column = pos
        if row >= 0 and row < self.rows and column >= 0 and column < self.columns:
            index = row * self.columns + column
            if index >= 0 and index < len(self._values):
                return self._values[index]

        return self.nodata

    def __setitem__(self, pos, value):
        """Array index assignment operator for Raster
        """
        row, column = pos
        if row >= 0 and row < self.rows and column >= 0 and column < self.columns:
            index = row * self.columns + column
            if index >= 0 and index < len(self._values):
                self._values[index] = value

    # def __delitem__(self, pos):
    #     row, column = pos
    #     # do nothing; this should be allowable

    def __iadd__(self, other):
        """Increment (+=) operator for Raster
        """
        if type(other) is Raster:
            if self.rows != other.rows or self.columns != other.columns:
                raise Exception("Both rasters must have the same dimensions.")

            for i in range(self.rows * self.columns):
                # row = int(math.floor(float(i) / float(self.columns)))
                # col = int(float(i) % float(self.columns))
                self._values[i] += other._values[i]  # [row, col]

        elif (type(other) is int) or (type(other) is float):
            for i in range(self.rows * self.columns):
                self._values[i] += float(other)

        return self

    def __isub__(self, pos, value):
        """Decrement (-=) operator for Raster
        """
        if type(other) is Raster:
            if self.rows != other.rows or self.columns != other.columns:
                raise Exception("Both rasters must have the same dimensions.")

            for i in range(self.rows * self.columns):
                # row = int(math.floor(float(i) / float(self.columns)))
                # col = int(float(i) % float(self.columns))
                self._values[i] -= other._values[i]  # [row, col]

        elif (type(other) is int) or (type(other) is float):
            for i in range(self.rows * self.columns):
                self._values[i] -= float(other)

        return self

    def __itruediv__(self, other):
        """Increment (/=) operator for Raster
        """
        if type(other) is Raster:
            if self.rows != other.rows or self.columns != other.columns:
                raise Exception("Both rasters must have the same dimensions.")

            for i in range(self.rows * self.columns):
                # row = int(math.floor(float(i) / float(self.columns)))
                # col = int(float(i) % float(self.columns))
                self._values[i] /= other._values[i]  # [row, col]

        elif (type(other) is int) or (type(other) is float):
            for i in range(self.rows * self.columns):
                self._values[i] /= float(other)

        return self

    def __imul__(self, other):
        """Increment (*=) operator for Raster
        """
        if type(other) is Raster:
            if self.rows != other.rows or self.columns != other.columns:
                raise Exception("Both rasters must have the same dimensions.")

            for i in range(self.rows * self.columns):
                # row = int(math.floor(float(i) / float(self.columns)))
                # col = int(float(i) % float(self.columns))
                self._values[i] *= other._values[i]  # [row, col]

        elif (type(other) is int) or (type(other) is float):
            for i in range(self.rows * self.columns):
                self._values[i] *= float(other)

        return self

    def __add__(self, other):
        """Add two Raster
        """
        if type(other) is Raster:
            if self.rows != other.rows or self.columns != other.columns:
                raise Exception("Both rasters must have the same dimensions.")

            for i in range(self.rows * self.columns):
                if self._values[i] != self.nodata or other._values[i] != other.nodata:
                    self._values[i] += other._values[i]

        elif (type(other) is int) or (type(other) is float):
            for i in range(self.rows * self.columns):
                if self._values[i] != self.nodata:
                    self._values[i] += other

        return self

    def __mul__(self, other):
        """Add two Raster
        """
        if type(other) is Raster:
            if self.rows != other.rows or self.columns != other.columns:
                raise Exception("Both rasters must have the same dimensions.")

            for i in range(self.rows * self.columns):
                if self._values[i] != self.nodata or other._values[i] != other.nodata:
                    self._values[i] *= other._values[i]

        elif (type(other) is int) or (type(other) is float):
            for i in range(self.rows * self.columns):
                if self._values[i] != self.nodata:
                    self._values[i] *= other

        return self

    def __eq__(self, other):
        if isinstance(other, Raster):
            if self.rows != other.rows or self.columns != other.columns:
                return False

            for i in range(self.rows * self.columns):
                if self._values[i] != other._values[i]:
                    return False

            return True
        return NotImplemented

    def read(self):
        # First, read the header file
        self.metadata = []
        with open(self.header_filename) as fp:
            line = fp.readline()
            while line:
                line = line.strip()
                if 'min:' in line.lower() and not 'display' in line.lower():
                    self.minimum = float(line.split(':')[1].strip())
                elif 'max:' in line.lower() and not 'display' in line.lower():
                    self.maximum = float(line.split(':')[1].strip())
                elif 'display min:' in line.lower():
                    self.display_minimum = float(line.split(':')[1].strip())
                elif 'display max:' in line.lower():
                    self.display_maximum = float(line.split(':')[1].strip())
                elif 'north:' in line.lower():
                    self.north = float(line.split(':')[1].strip())
                elif 'south:' in line.lower():
                    self.south = float(line.split(':')[1].strip())
                elif 'east:' in line.lower():
                    self.east = float(line.split(':')[1].strip())
                elif 'west:' in line.lower():
                    self.west = float(line.split(':')[1].strip())
                elif 'rows:' in line.lower():
                    self.rows = int(line.split(':')[1].strip())
                elif 'cols:' in line.lower():
                    self.columns = int(line.split(':')[1].strip())
                elif 'stacks:' in line.lower():
                    self.stacks = int(line.split(':')[1].strip())
                elif 'data type:' in line.lower():
                    self.data_type = line.split(':')[1].strip().lower()
                elif 'z units:' in line.lower():
                    self.z_units = line.split(':')[1].strip()
                elif 'xy units:' in line.lower():
                    self.xy_units = line.split(':')[1].strip()
                elif 'projection:' in line.lower():
                    self.projection = line.split(':')[1].strip()
                elif 'data scale:' in line.lower():
                    self.data_scale = line.split(':')[1].strip().lower()
                elif 'preferred palette:' in line.lower():
                    self.palette = line.split(':')[1].strip()
                elif 'nodata:' in line.lower():
                    self.nodata = float(line.split(':')[1].strip())
                elif 'byte order:' in line.lower():
                    self.byte_order = line.split(':')[1].strip().lower()
                elif 'palette nonlinearity:' in line.lower():
                    self.palette_nonlinearity = float(
                        line.split(':')[1].strip())
                elif 'metadata' in line.lower():
                    self.metadata.append(line.split(':')[1].strip())
                else:
                    print(line)

                line = fp.readline()

        self.resolution_x = (self.east - self.west) / self.columns
        self.resolution_y = (self.north - self.south) / self.rows

        # self._values = [self._nodata]*self._rows*self._columns
        self._values = []
        num_pixels = self.rows * self.columns

        with open(self.data_filename, "rb") as binary_file:
            # Read the whole file at once
            data = binary_file.read()

            data_size = 4
            pack_format = ">"  # big endian
            if any(s in self.byte_order for s in ("little_endian", "least", "lsb", "little")):
                pack_format = "<"  # little endian

            if self.data_type == 'float':
                data_size = 4
                pack_format += "f"
            elif self.data_type == 'double':
                data_size = 8
                pack_format += "d"
            elif self.data_type == 'integer':
                data_size = 2
                pack_format += "h"
            elif self.data_type == 'byte':
                data_size = 1
                pack_format += "c"
            elif self.data_type == 'i32':
                data_size = 4
                pack_format += "i"
            else:
                raise Exception("Unknown data type")

            for p in range(num_pixels):
                # Seek position and read N bytes
                pos = p * data_size
                val, = struct.unpack(pack_format, data[pos:pos + data_size])
                self._values.append(val)

    def write(self):
        self.calculate_min_and_max()

        if self.display_maximum == float('-inf'):
            self.display_maximum = self.maximum

        if self.display_minimum == float('inf'):
            self.display_minimum = self.minimum

        # write the header data
        with open(self.header_filename, 'w') as header_file:
            header_file.write("Min:\t{}\n".format(self.minimum))
            header_file.write("Max:\t{}\n".format(self.maximum))
            header_file.write("North:\t{}\n".format(self.north))
            header_file.write("South:\t{}\n".format(self.south))
            header_file.write("East:\t{}\n".format(self.east))
            header_file.write("West:\t{}\n".format(self.west))
            header_file.write("Cols:\t{}\n".format(self.columns))
            header_file.write("Rows:\t{}\n".format(self.rows))
            header_file.write("Stacks:\t{}\n".format(self.stacks))
            header_file.write("Data Type:\t{}\n".format(self.data_type))
            header_file.write("Z Units:\t{}\n".format(self.z_units))
            header_file.write("XY Units:\t{}\n".format(self.xy_units))
            header_file.write("Projection:\t{}\n".format(self.projection))
            header_file.write("Data Scale:\t{}\n".format(self.data_scale))
            header_file.write(
                "Display Min:\t{}\n".format(self.display_minimum))
            header_file.write(
                "Display Max:\t{}\n".format(self.display_maximum))
            header_file.write("Preferred Palette:\t{}\n".format(
                self.palette.replace('.pal', '.plt')))
            header_file.write("NoData:\t{}\n".format(self.nodata))
            if any(s in self.byte_order for s in ("little_endian", "least", "lsb", "little")):
                header_file.write("Byte Order:\tLITTLE_ENDIAN\n")
            else:
                header_file.write("Byte Order:\tBIG_ENDIAN\n")
            header_file.write("Palette Nonlinearity:\t{}\n".format(
                self.palette_nonlinearity))
            for v in self.metadata:
                header_file.write(
                    "Metadata Entry:\t{}\n".format(v.replace(":", ";")))

        # write the binary data
        with open(self.data_filename, "wb") as binary_file:
            data_size = 4
            pack_format = ">"  # big endian
            if any(s in self.byte_order for s in ("little_endian", "least", "lsb", "little")):
                pack_format = "<"  # little endian

            if self.data_type == 'float':
                data_size = 4
                pack_format += "f"
            elif self.data_type == 'double':
                data_size = 8
                pack_format += "d"
            elif self.data_type == 'integer':
                data_size = 2
                pack_format += "h"
            elif self.data_type == 'byte':
                data_size = 1
                pack_format += "c"
            elif self.data_type == 'i32':
                data_size = 4
                pack_format += "i"
            else:
                raise Exception("Unknown data type")

            data = bytearray()
            num_pixels = self.rows * self.columns
            for p in range(num_pixels):
                vals = struct.pack(pack_format, self._values[p])
                data.extend(vals)

            binary_file.write(data)

    def calculate_min_and_max(self):
        """ Figure out the minimum and maximum values
        """
        for i in range(self.rows * self.columns):
            z = self._values[i]
            if z != self.nodata:
                if z < self.minimum:
                    self.minimum = z
                if z > self.maximum:
                    self.maximum = z

    def get_x_from_column(self, column):
        return self.west + self.resolution_x / 2.0 + column * self.resolution_x

    def get_y_from_row(self, row):
        return self.north - self.resolution_y / 2.0 - row * self.resolution_y

    def get_column_from_x(self, x):
        return math.floor((x - self.west) / self.resolution_x)

    def get_row_from_y(self, y):
        return math.floor((self.north - y) / self.resolution_y)


class Array2D(object):
    @staticmethod
    def create(rows, columns, nodata=-32768.0, initial_value=None):
        """ Constructor for Array2D
        """
        a2d = Array2D()
        a2d.rows = rows
        a2d.columns = columns
        a2d.nodata = nodata
        if initial_value is None:
            a2d._values = [nodata] * rows * columns
        else:
            a2d._values = [initial_value] * rows * columns

        return a2d

    def __getitem__(self, pos):
        """Array indexing operator for Array2D
        """
        row, column = pos
        if row >= 0 and row < self.rows and column >= 0 and column < self.columns:
            index = row * self.columns + column
            if index >= 0 and index < len(self._values):
                return self._values[index]

        return self.nodata

    def __setitem__(self, pos, value):
        """Array index assignment operator for Array2D
        """
        row, column = pos
        if row >= 0 and row < self.rows and column >= 0 and column < self.columns:
            index = row * self.columns + column
            if index >= 0 and index < len(self._values):
                self._values[index] = value
