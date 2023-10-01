from datetime import datetime, timedelta, date
import pyodbc
import traceback
from flask import Flask, render_template, jsonify , json

app = Flask(__name__)

conn_str = (
    r'DRIVER={SQL Server};'
    r'SERVER=DESKTOP-17KP3L2;'
    r'DATABASE=PlateMill23;'
    r'LoginTimeout=30;'
)
specific_date = datetime(2023, 7, 27)

# Database connection
def get_db_connection():
    return pyodbc.connect(conn_str)

@app.route('/')
def load():
    try:
        with get_db_connection() as conn:
            #specific_date = datetime(2023, 7, 27)
            yesterday = specific_date - timedelta(days=1)
            #start_date = end_date = yesterday.strftime('%d/%m/%Y')

            cursor = conn.cursor()
            query = f"""SELECT	Dateprod,  percentage_chute 
                        FROM	Kpis_platemill
                        WHERE	Dateprod = convert(datetime , ?)
                        ORDER BY Dateprod"""
            
            query2 = """select sum(Poidsnet) as poidsnet_sum from dbo.Production$ where DateP = convert(datetime ,?)"""
            cursor.execute(query , yesterday)
            data = cursor.fetchall()

            cursor.execute(query2 , yesterday)
            data2 =  cursor.fetchone()
       
        result = [{'Dateprod': row.Dateprod, 'percentage_chute': row.percentage_chute, 'poidsnet_sum': data2[0]} for row in data]
        
        #json_result = json.dumps(result)
        return render_template ('index.html',data=result)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, 500 


@app.route('/j_1')
def get_yesterday():
    try:
        with get_db_connection() as conn:
            #specific_date = datetime(2023, 7, 27)
            yesterday = specific_date - timedelta(days=1)
            #start_date = end_date = yesterday.strftime('%d/%m/%Y')

            cursor = conn.cursor()
            query = f"""SELECT	Dateprod, poidsnet_sum, percentage_chute 
                        FROM	Kpis_platemill
                        WHERE	Dateprod = convert(datetime , ?)
                        ORDER BY Dateprod"""
            query2 = """select sum(Poidsnet) as poidsnet_sum from dbo.Production$ where DateP = convert(datetime ,?)"""
            cursor.execute(query , yesterday)
            data = cursor.fetchall()

            cursor.execute(query2 , yesterday)
            data2 =  cursor.fetchone()
        result = [{'Dateprod': row.Dateprod, 'percentage_chute': row.percentage_chute, 'poidsnet_sum': data2[0]} for row in data]
        
        return result

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, 500 

@app.route('/s_1')
def get_last_week():
    try:
        
        with get_db_connection() as conn:
            start_date = specific_date - timedelta(days=specific_date.weekday() + 7)
            end_date = start_date + timedelta(days=6)

            cursor = conn.cursor()
            query = f"""SELECT	Dateprod, percentage_chute 
                        FROM	Kpis_platemill
                        WHERE	Dateprod >= convert(datetime , ?) and Dateprod <= convert(datetime , ?)
                        ORDER BY Dateprod"""
            query2 = """SELECT  sum(Poidsnet) as poidsnet_sum  , DateP
                        FROM    dbo.Production$
                        WHERE	DateP >= convert(datetime , ?) and DateP <= convert(datetime , ?)
                        group BY DateP
                        order by DateP"""
            cursor.execute(query , start_date, end_date)
            data = cursor.fetchall()

            cursor.execute(query2 , start_date, end_date)
            data2 =  cursor.fetchall()
        
        result = [{'Dateprod':  row.Dateprod,'percentage_chute': row.percentage_chute, 'poidsnet_sum':data2_item[0]} for row , data2_item in zip(data, data2)]
        
        return result

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, 500

@app.route('/mois')
def get_month():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = f"""SELECT	Dateprod, poidsnet_sum, percentage_chute 
                        FROM	Kpis_platemill
                        WHERE	 MONTH(Dateprod) = ?
                        ORDER BY Dateprod"""
           
            query2 = """SELECT  sum(Poidsnet) as poidsnet_sum  , DateP
                        FROM    dbo.Production$
                        WHERE	MONTH(DateP) = ?
                        group BY DateP
                        order by DateP"""
            cursor.execute(query , specific_date.month)
            data = cursor.fetchall()

            cursor.execute(query2 , specific_date.month)
            data2 =  cursor.fetchall()
        print(data)
        result = [{'Dateprod':  row.Dateprod,'percentage_chute': row.percentage_chute, 'poidsnet_sum':data2_item[0]} for row , data2_item in zip(data, data2)]
        
        return result
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, 500  

@app.route('/annee')
def get_annee():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = f"""SELECT  AVG(percentage_chute) AS avg_percentage_chute ,Month(Dateprod) as months
                        FROM    Kpis_platemill
                        WHERE   YEAR(Dateprod) = ?
                        GROUP BY Month(Dateprod)
                        ORDER BY months"""

            query2 = f"""SELECT sum(Poidsnet) as poidsnet_sum , MONTH(DateP) AS months
                        FROM dbo.Production$
                        WHERE   YEAR(DateP) = ?
                        GROUP BY Month(DateP)
                        ORDER BY months"""
           
            cursor.execute(query, specific_date.year)
            data = cursor.fetchall()
            print("data ",data)
            
            cursor.execute(query2 ,specific_date.year)
            data2 =  cursor.fetchall()
            for row in data:
                print(type(row.months))
        result = [{'Dateprod': date(specific_date.year,int(row.months), 1) if row.months  is not None else None, 'percentage_chute': row.avg_percentage_chute, 'poidsnet_sum': data2_item.poidsnet_sum} for row, data2_item in zip(data, data2)]
        print("result ", result)
        return result

    except Exception as e:
        traceback.print_exc()
        error_message = f"An error occurred: {str(e)}"
        return error_message, 500 

@app.route('/search')
def get_search():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = f"""SELECT	Dateprod, poidsnet_sum, percentage_chute 
                        FROM	Kpis_platemill
                        WHERE	Dateprod >= convert(datetime , ?) and Dateprod <= convert(datetime , ?)
                        ORDER BY Dateprod"""
            cursor.execute(query , start_date , end_date)
            data = cursor.fetchall()

        return render_template('index.html', data=data)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, 500 

if __name__ == '__main__':
    app.run(debug=True)  
