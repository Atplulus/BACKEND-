import serial 
import mysql.connector 
import time 

ser = serial.Serial()
mysql_connection = mysql.connector.connect(
    host = "",
    user = "",
    password = "",
    database = ""
)
cursor = mysql_connection.cursor()
direction = 1  # 1 untuk searah, -1 untuk berbalik arah
threshold_value = 0  # Nilai ambang batas untuk mengubah arah
while True:
    data = ser.readline().decode("utf-8")
    #print(data, end="")
    separated_data = data.split(',')

    # Cek apakah ada dua elemen setelah pemisahan
    if len(separated_data) == 2:
        unit = separated_data[0].strip()  # Menghapus spasi ekstra
        value = float(separated_data[1])  # Mengonversi nilai menjadi float
        print("Unit:", unit)
        print("Value:", value)
         # Logika untuk mengubah arah
        if value > threshold_value:
            direction = 1  # Mengarah ke depan
        elif value < 0:
            direction = -1  # Kecepatan dari kiri ke kanan

        # Lakukan sesuatu berdasarkan arah yang ditentukan
        if direction == 1:
            print("Moving forward")
            # Lakukan sesuatu untuk pergerakan ke depan
        elif direction == -1:
            print("Moving Backward")
            # Lakukan sesuatu untuk pergerakan dari kiri ke kanan
            sql_query = "INSERT INTO your_table (unit, value, direction) VALUES (%s, %s, %s)"
            data_tuple = (unit, value, direction)

            # Execute the SQL query
            cursor.execute(sql_query, data_tuple)
            mysql_connection.commit()
            print(f"Unit: {unit}, Value: {value}, Direction: {direction}")
    # Tunggu selama 1 detik
    time.sleep(1)

