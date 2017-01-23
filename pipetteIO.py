import json

def save_calibration_data(path,coordinate):
        #check this section again. This may need quite some buffer as the calibration data is deleted and recreated during every calibration
        #need to have error checking code
        try:
            with open(path,'r') as calibration:
                old_data = calibration.read()
                new_data = json.loads(old_data)
                for each in coordinate:
                    if each in new_data:
                        del new_data[each]
                new_data.update(coordinate)
        except IOError:
            new_data = coordinate

        with open(path,'w') as calibration:
            s = json.dumps(new_data)
            calibration.write(s)

def read_calibration_data(path,name):
    with open(path,'r') as calibration:
        data = json.loads(calibration.read())
        if name in data:
            return data[name]
        else:
            return None

def main():
    pass

if __name__ == '__main__':
    main()
