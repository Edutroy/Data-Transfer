from flask import Flask, render_template, request, redirect, url_for, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import SpreadsheetNotFound

app = Flask(__name__)

# Configura las credenciales de Google Sheets
def conexion():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('./credencial.json', scope)
        client = gspread.authorize(creds)
        return client
    except FileNotFoundError:
         return redirect(url_for('error'))
    
    

def get_data_from_sheet():
    try:
        client = conexion() 
        worksheet = client.open('FLASKconexion').sheet1
        data = worksheet.get_all_records()
        return data
    except SpreadsheetNotFound:
        # Si la hoja de cálculo no se encuentra, lanza una excepción personalizada
        raise Exception("La hoja de cálculo no se encontró")

@app.route('/')
def index():
    try:
        # Obtiene los datos de la hoja de cálculo
        data = get_data_from_sheet()
        return render_template('index.jinja', data=data)
    except Exception as e:
        # Captura la excepción personalizada y redirige a la página de error
        return redirect(url_for('error', message=str(e)))

@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    try:
        # Obtiene los datos de la hoja de cálculo y los devuelve en formato JSON
        data = get_data_from_sheet()
        return jsonify(data)
    except Exception as e:
        # Captura la excepción personalizada y redirige a la página de error
        return redirect(url_for('error', message=str(e)))

@app.route('/error')
def error():
    message = request.args.get('message', 'Error desconocido')
    return render_template('error.jinja', message=message)

@app.errorhandler(404)
def page_not_found(e):
    # Página personalizada para errores 404
    message = request.args.get('message', 'Error 404')
    return render_template('error.jinja', message=message), 404

@app.errorhandler(500)
def internal_server_error(e):
    # Renderiza la página de error personalizada
    message = request.args.get('message', 'Error 500')
    return render_template('error.jinja', message=message), 500


if __name__ == '__main__':
    app.run(debug=True)
