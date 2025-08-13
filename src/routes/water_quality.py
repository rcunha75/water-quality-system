from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
import io
import os
from werkzeug.utils import secure_filename

water_quality_bp = Blueprint('water_quality', __name__)

# Configurações para upload
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_water_quality_index(df):
    """
    Calcula um índice de qualidade da água baseado nos parâmetros disponíveis.
    Como não temos todos os parâmetros do IQA tradicional, criamos um índice adaptado.
    """
    results = {}
    
    # Análise dos parâmetros disponíveis
    if 'pH' in df.columns:
        ph_values = df['pH'].dropna()
        # pH ideal entre 6.5 e 8.5
        ph_score = []
        for ph in ph_values:
            if 6.5 <= ph <= 8.5:
                ph_score.append(100)
            elif 6.0 <= ph < 6.5 or 8.5 < ph <= 9.0:
                ph_score.append(80)
            elif 5.5 <= ph < 6.0 or 9.0 < ph <= 9.5:
                ph_score.append(60)
            elif 5.0 <= ph < 5.5 or 9.5 < ph <= 10.0:
                ph_score.append(40)
            else:
                ph_score.append(20)
        results['ph_score'] = np.mean(ph_score) if ph_score else 0
    
    # Análise da temperatura
    if 'Temperature(°C)' in df.columns:
        temp_values = df['Temperature(°C)'].dropna()
        # Temperatura ideal entre 15-25°C para águas naturais
        temp_score = []
        for temp in temp_values:
            if 15 <= temp <= 25:
                temp_score.append(100)
            elif 10 <= temp < 15 or 25 < temp <= 30:
                temp_score.append(80)
            elif 5 <= temp < 10 or 30 < temp <= 35:
                temp_score.append(60)
            else:
                temp_score.append(40)
        results['temp_score'] = np.mean(temp_score) if temp_score else 0
    
    # Análise do TDS (Total Dissolved Solids)
    if 'TDS' in df.columns:
        tds_values = df['TDS'].dropna()
        # TDS ideal < 500 mg/L para água potável
        tds_score = []
        for tds in tds_values:
            if tds < 300:
                tds_score.append(100)
            elif 300 <= tds < 500:
                tds_score.append(80)
            elif 500 <= tds < 1000:
                tds_score.append(60)
            elif 1000 <= tds < 2000:
                tds_score.append(40)
            else:
                tds_score.append(20)
        results['tds_score'] = np.mean(tds_score) if tds_score else 0
    
    # Análise da Condutividade Elétrica
    if 'EC' in df.columns:
        ec_values = df['EC'].dropna()
        # EC ideal < 750 µS/cm para água potável
        ec_score = []
        for ec in ec_values:
            if ec < 250:
                ec_score.append(100)
            elif 250 <= ec < 750:
                ec_score.append(80)
            elif 750 <= ec < 1500:
                ec_score.append(60)
            elif 1500 <= ec < 3000:
                ec_score.append(40)
            else:
                ec_score.append(20)
        results['ec_score'] = np.mean(ec_score) if ec_score else 0
    
    # Cálculo do índice geral (média ponderada)
    scores = [v for v in results.values() if v > 0]
    if scores:
        overall_index = np.mean(scores)
        
        # Classificação do índice
        if overall_index >= 90:
            classification = "Excelente"
        elif overall_index >= 70:
            classification = "Boa"
        elif overall_index >= 50:
            classification = "Regular"
        elif overall_index >= 25:
            classification = "Ruim"
        else:
            classification = "Muito Ruim"
        
        results['overall_index'] = overall_index
        results['classification'] = classification
    else:
        results['overall_index'] = 0
        results['classification'] = "Dados insuficientes"
    
    return results

@water_quality_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            # Criar diretório de upload se não existir
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Ler o arquivo Excel diretamente da memória
            df = pd.read_excel(file)
            
            # Análise básica dos dados
            data_info = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': df.columns.tolist(),
                'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'missing_values': df.isnull().sum().to_dict(),
                'sample_data': df.head().to_dict('records')
            }
            
            # Estatísticas descritivas
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                data_info['statistics'] = df[numeric_columns].describe().to_dict()
            
            # Cálculo do índice de qualidade da água
            water_quality_index = calculate_water_quality_index(df)
            
            return jsonify({
                'success': True,
                'data_info': data_info,
                'water_quality_index': water_quality_index,
                'message': 'Arquivo processado com sucesso'
            })
        
        return jsonify({'error': 'Tipo de arquivo não permitido. Use apenas .xlsx ou .xls'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 500

@water_quality_bp.route('/parameters', methods=['GET'])
def get_parameters_info():
    """Retorna informações sobre os parâmetros de qualidade da água"""
    parameters_info = {
        'iqa_standard_parameters': [
            'Temperatura da Água',
            'pH',
            'Oxigênio Dissolvido (OD)',
            'Demanda Bioquímica de Oxigênio (DBO)',
            'Coliformes Termotolerantes',
            'Nitrogênio Total',
            'Fósforo Total',
            'Turbidez',
            'Resíduo Total (Sólidos Totais)'
        ],
        'available_parameters': [
            'Date',
            'EC (Condutividade Elétrica)',
            'TDS (Sólidos Totais Dissolvidos)',
            'SALT(TDS) (Salinidade baseada em TDS)',
            'SALT(S.G.) (Salinidade baseada em Gravidade Específica)',
            'pH',
            'ORP(mV) (Potencial de Oxirredução)',
            'Temperature(°C)'
        ],
        'parameter_ranges': {
            'pH': {
                'excellent': '6.5 - 8.5',
                'good': '6.0 - 6.5 ou 8.5 - 9.0',
                'regular': '5.5 - 6.0 ou 9.0 - 9.5',
                'poor': '5.0 - 5.5 ou 9.5 - 10.0',
                'very_poor': '< 5.0 ou > 10.0'
            },
            'Temperature': {
                'excellent': '15 - 25°C',
                'good': '10 - 15°C ou 25 - 30°C',
                'regular': '5 - 10°C ou 30 - 35°C',
                'poor': '< 5°C ou > 35°C'
            },
            'TDS': {
                'excellent': '< 300 mg/L',
                'good': '300 - 500 mg/L',
                'regular': '500 - 1000 mg/L',
                'poor': '1000 - 2000 mg/L',
                'very_poor': '> 2000 mg/L'
            },
            'EC': {
                'excellent': '< 250 µS/cm',
                'good': '250 - 750 µS/cm',
                'regular': '750 - 1500 µS/cm',
                'poor': '1500 - 3000 µS/cm',
                'very_poor': '> 3000 µS/cm'
            }
        }
    }
    
    return jsonify(parameters_info)

@water_quality_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({'status': 'OK', 'message': 'API de Qualidade da Água funcionando'})

