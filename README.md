# Sistema de Análise de Qualidade da Água

## Descrição
Sistema web completo para análise de qualidade da água com upload de arquivos Excel e dashboard interativo.

## Tecnologias
- Backend: Flask (Python)
- Frontend: React
- Análise de dados: Pandas, NumPy
- Visualização: Recharts

## Deploy no Render.com

### Pré-requisitos
1. Conta no GitHub
2. Conta no Render.com

### Passos para Deploy
1. Faça fork ou clone este repositório
2. Conecte sua conta GitHub ao Render.com
3. Crie um novo Web Service no Render
4. Selecione este repositório
5. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment: Python 3

### Funcionalidades
- Upload de arquivos Excel (.xlsx, .xls)
- Cálculo automático do índice de qualidade da água
- Dashboard interativo com gráficos
- Análise detalhada por parâmetros

## Estrutura do Projeto
```
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── Procfile           # Configuração para deploy
├── render.yaml        # Configuração específica do Render
├── runtime.txt        # Versão do Python
├── src/
│   ├── routes/        # Rotas da API
│   ├── static/        # Arquivos do frontend React
│   └── models/        # Modelos de dados
└── README.md          # Este arquivo
```

## Uso
1. Acesse o site implantado
2. Faça upload de um arquivo Excel com dados de qualidade da água
3. Visualize os resultados no dashboard interativo

