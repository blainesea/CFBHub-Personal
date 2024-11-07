import os

def getNames():
    directoryPath = "footballSchedules"
    if not os.path.isdir(directoryPath):
        print(f"The path '{directoryPath}' is not a valid directory.")
        return []

    files = [
        os.path.splitext(f)[0]
        for f in os.listdir(directoryPath)
        if os.path.isfile(os.path.join(directoryPath, f)) and f.endswith('.csv')
    ]
    return files


# directoryPath = "football_schedules"
# files = getNames()
# if files:
#     print("CSV Files:", files)