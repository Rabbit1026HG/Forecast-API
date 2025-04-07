from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pmdarima as pm
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from datetime import timedelta

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided', 'status': 'error'}), 400
        
        # Validate sales_data
        if 'sales_data' not in data:
            return jsonify({'error': 'sales_data is required', 'status': 'error'}), 400
        sales_data = data['sales_data']
        if not isinstance(sales_data, list):
            return jsonify({'error': 'sales_data must be an array', 'status': 'error'}), 400
        if len(sales_data) < 31:
            return jsonify({'error': 'sales_data must contain at least 31 points', 'status': 'error'}), 400
        if not all(isinstance(x, (int, float)) for x in sales_data):
            return jsonify({'error': 'sales_data must contain only numbers', 'status': 'error'}), 400

        # Validate prediction_length
        prediction_length = data.get('prediction_length', 30)        
        if not isinstance(prediction_length, int):
            return jsonify({'error': 'prediction_length must be an integer', 'status': 'error'}), 400
        if prediction_length <= 0:
            return jsonify({'error': 'prediction_length must be positive', 'status': 'error'}), 400
        
        model = pm.auto_arima(
            sales_data, 
            seasonal=True, 
            m=12
        )


        predictions = model.predict(prediction_length)
        forecasts = [round(float(value), 2) for value in predictions]

        return jsonify({
            'prediction': forecasts,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 400

@app.route('/irregular_predict', methods=['POST'])
def irregular_predict():
    try:
        # Get JSON data from POST request
        json_data = request.get_json()
        
        # Convert JSON to DataFrame
        if not json_data or 'data' not in json_data:
            return jsonify({'error': 'No data provided', 'status': 'error'}), 400
        
        prediction_length = json_data.get('prediction_length', 30)
        
        if not isinstance(prediction_length, int):
            return jsonify({'error': 'prediction_length must be an integer', 'status': 'error'}), 400

        if prediction_length <= 0:
            return jsonify({'error': 'prediction_length must be positive', 'status': 'error'}), 400
        
        df = pd.DataFrame(json_data['data'])
        
        # Ensure Date column is parsed as datetime and set as index
        if 'Date' not in df.columns or 'Amount' not in df.columns:
            return jsonify({'error': 'Invalid data format', 'status': 'error'}), 400
        
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        # Resample and interpolate the data
        daily_data = df.resample('D').mean()
        
        # Check if DataFrame has minimum required length
        if len(daily_data) < 32:
            return jsonify({'error': 'Data must contain at least 32 points', 'status': 'error'}), 400

        daily_resampled_data = daily_data.interpolate(method='linear')
        forecast_data = daily_resampled_data.iloc[-80:] if len(daily_resampled_data) >= 80 else daily_resampled_data
        
        # Fit the ARIMA model and generate predictions
        model = pm.auto_arima(
            forecast_data, 
            seasonal=True, 
            m=12
        )
        predictions = model.predict(prediction_length)
        
        # Create predictions DataFrame
        last_date = daily_resampled_data.index[-1]
        actualSpend = daily_resampled_data.iloc[-1]['Amount'].round(2)
        prediction_dates = pd.date_range(start=last_date + timedelta(days=1), periods=prediction_length)
        predictions_df = pd.DataFrame(predictions, index=prediction_dates, columns=daily_resampled_data.columns)
        forecastAmount = predictions_df['Amount'].mean().round(2)         
        
        # Prepare response data
        response_data = {
            'actualSpend': actualSpend,
            'forecastAmount': forecastAmount,
            'forecasts': {k.strftime('%Y-%m-%d'): v for k, v in predictions_df['Amount'].round(2).to_dict().items()},            
            'status': 'success'
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 400

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)

