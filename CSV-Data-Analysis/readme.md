# 📊 CSV Data Analyzer with LangChain & Ollama

An intelligent CSV data analysis tool that lets you explore and analyze your data using natural language queries. Built with LangChain, Ollama (Llama2), and Streamlit for a seamless data analysis experience.



## ✨ Features

- 📤 **Easy CSV Upload**: Drag and drop your CSV files for instant analysis
- 📊 **Interactive Visualizations**: Generate histograms, scatter plots, bar charts, line charts, and correlation heatmaps
- 🔍 **Comprehensive Data Overview**: Automatic data profiling and summary statistics
- 🤖 **AI-Powered Analysis**: Powered by Llama2 running locally via Ollama
- 🔒 **Privacy First**: Your data stays on your machine - no external API calls
- 📱 **Responsive Design**: Clean, modern interface built with Streamlit
- ☁️ **Cloud Deployed**: Available online via Streamlit Community Cloud

## 🌐 Live Demo vs Local Setup

**🌍 Streamlit Cloud Version**: 
- Full data analysis and visualization features
- CSV upload and processing
- Interactive charts and data summaries
- No natural language querying (requires local Ollama setup)

**💻 Local Setup**:
- All cloud features PLUS natural language AI queries
- Complete LangChain + Ollama integration
- Ask questions like "What's the correlation between sales and revenue?"

## 🛠️ Technologies Used

- **LangChain** - For building the AI agent and data processing pipeline
- **Ollama** - Local LLM runtime for Llama2
- **Streamlit** - Web application framework and hosting
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive data visualizations
- **NumPy** - Numerical computing

## 🚀 Quick Start

### Option 1: Try Online (Instant)
Just visit **[AnalytiCSV.streamlit.app](https://analyticsv.streamlit.app/)** and start analyzing your CSV files immediately!

### Option 2: Run Locally (Full Features)

#### Prerequisites for Local Setup

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull Llama2 model**:
   ```bash
   ollama pull llama2
   ```

3. **Python Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

#### Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Revati-N/Langchain_Projects.git
   cd csv-data-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit pandas numpy langchain-ollama langchain-experimental matplotlib seaborn plotly
   ```

3. **Start Ollama service**:
   ```bash
   ollama serve
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 📋 Requirements

Create a `requirements.txt` file with:

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
langchain-ollama>=0.1.0
langchain-experimental>=0.0.45
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0
```

## 🎯 How It Works

### Online Version:
1. **Visit the App**: Go to the Streamlit Cloud deployment
2. **Upload Your Data**: Use the sidebar to upload any CSV file
3. **Explore Overview**: View your data structure, column types, and missing values
4. **Create Visualizations**: Generate interactive charts with just a few clicks
5. **Download Results**: Export your processed data for further analysis

### Local Version (Additional Features):
6. **Ask Natural Language Questions**: Query your data using plain English
7. **AI-Powered Insights**: Get intelligent analysis powered by Llama2

## 📊 Supported Visualizations

- **Histograms** - Distribution analysis for numerical columns
- **Scatter Plots** - Relationship between two numerical variables
- **Bar Charts** - Categorical data visualization
- **Line Charts** - Trend analysis over time or ordered data
- **Correlation Heatmaps** - Visual correlation matrix for numerical features

## 🔧 Configuration

The app automatically configures itself, but you can customize:

- **LLM Temperature**: Adjust in the `initialize_llm()` function
- **Model Selection**: Change from `llama2` to any other Ollama model
- **Visualization Themes**: Modify Plotly themes in visualization functions

## 🚀 Deployment

This app is deployed on **Streamlit Community Cloud**. To deploy your own version:

1. Fork this repository
2. Connect your GitHub account to Streamlit
3. Deploy directly from your repository
4. Your app will be available at `https://analyticsv.streamlit.app/`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** team for the amazing framework
- **Ollama** for making local LLMs accessible
- **Streamlit** for the beautiful web framework and free hosting
- **Meta** for the Llama2 model

## 📞 Support

**For Online Version Issues**:
- Check your CSV file format
- Ensure file size is reasonable for browser upload

**For Local Setup Issues**:
1. Check if Ollama is running: `ollama list`
2. Ensure Llama2 model is installed: `ollama pull llama2`
3. Verify all dependencies are installed: `pip list`

For bugs and feature requests, please create an issue on GitHub.

***

⭐ **If you found this project helpful, please give it a star!** ⭐

🌐 **Try it now**: [AnalytiCSV](https://analyticsv.streamlit.app/)

Built with ❤️ as part of #14Days14LangChainProjects challenge
