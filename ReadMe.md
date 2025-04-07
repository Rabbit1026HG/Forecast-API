# Sales Prediction API

This project is a RESTful API built using Flask to perform time-series forecasting on sales data. It supports both regular and irregular time series data using ARIMA models for prediction.

## Features

- **Sales Prediction**: Predict future sales based on historical data.
- **Support for Irregular Data**: Handles data with irregular time intervals by resampling it to daily frequency.
- **Customizable Prediction Length**: Allows specifying the number of days to forecast.
- **CORS Enabled**: Cross-Origin Resource Sharing is enabled to allow requests from different origins.

## Endpoints

### `/predict` (POST)

Predicts future sales based on regular interval sales data.

#### Request Body

- `sales_data` (list of numbers, required): Historical sales data points.
- `prediction_length` (integer, optional): Number of future periods to predict. Default is 30.

#### Example Request

```json
{
  "sales_data": [100, 150, 200, 250, ...],
  "prediction_length": 30
}
```

#### Response

- `prediction`: List of predicted sales values.
- `status`: Success or error status message.

### `/irregular_predict` (POST)

Predicts future sales based on irregular interval sales data.

#### Request Body

- `data`: List containing objects with `Date` and `Amount`.
- `prediction_length` (integer, optional): Number of future periods to predict. Default is 30.

#### Example Request

```json
{
  "data": [
    {"Date": "2023-01-01", "Amount": 100},
    {"Date": "2023-01-05", "Amount": 150},
    ...
  ],
  "prediction_length": 30
}
```

#### Response

- `actualSpend`: Last observed spend amount.
- `forecastAmount`: Average of predicted amounts.
- `forecasts`: Predicted amounts mapped to future dates.
- `status`: Success or error status message.

#### Example Response
```json
{
    "actualSpend": 205.75,
    "forecastAmount": 210.45,
    "forecasts": {
        "2023-02-01": 215.30,
        ...
    },
    "status": "success"
}
```

## Installation

1. **Clone the Repository**

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Run the Application

Execute the following command in the terminal:

```bash
python app.py
```

The server will start and listen on port `5000`.

## Deployment

Deployment is done using Waitress web server, which is production-ready. Ensure that your environment meets the dependencies specified in `requirements.txt`.

Execute the following command in the terminal:

```bash
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## Error Handling

Error messages are returned in JSON format when invalid data is provided or internal errors occur.

## Contributing

Feel free to submit pull requests for additional features or bug fixes. Open issues for any bugs discovered as well.

## License

This project is licensed under the terms and conditions provided in the LICENSE file.

---

**Note:** This API requires Python 3.6+ and expects JSON formatted requests and responses. Usage of this software assumes basic understanding of Flask and ARIMA time-series forecasting.