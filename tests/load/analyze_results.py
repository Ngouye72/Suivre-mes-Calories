import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from typing import Dict, List, Tuple
from datetime import datetime

class LoadTestAnalyzer:
    def __init__(self, report_dir: str):
        self.report_dir = Path(report_dir)
        self.stats_file = None
        self.history_file = None
        self.failures_file = None
        
    def load_latest_results(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Charge les derniers résultats de test"""
        # Trouve les fichiers les plus récents
        stats_files = list(self.report_dir.glob("*_stats.csv"))
        history_files = list(self.report_dir.glob("*_stats_history.csv"))
        failures_files = list(self.report_dir.glob("*_failures.csv"))
        
        if not stats_files or not history_files:
            raise FileNotFoundError("Fichiers de résultats non trouvés")
            
        self.stats_file = max(stats_files, key=lambda x: x.stat().st_mtime)
        self.history_file = max(history_files, key=lambda x: x.stat().st_mtime)
        self.failures_file = max(failures_files, key=lambda x: x.stat().st_mtime)
        
        stats_df = pd.read_csv(self.stats_file)
        history_df = pd.read_csv(self.history_file)
        failures_df = pd.read_csv(self.failures_file) if failures_files else pd.DataFrame()
        
        return stats_df, history_df, failures_df
        
    def analyze_performance(self, stats_df: pd.DataFrame) -> Dict:
        """Analyse les métriques de performance"""
        return {
            "total_requests": stats_df["Total Request Count"].sum(),
            "avg_response_time": stats_df["Average Response Time"].mean(),
            "median_response_time": stats_df["Median Response Time"].mean(),
            "p95_response_time": stats_df["95%"].mean(),
            "failures_percent": (stats_df["Failure Count"].sum() / stats_df["Total Request Count"].sum()) * 100,
            "requests_per_second": stats_df["Requests/s"].mean()
        }
        
    def analyze_endpoints(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        """Analyse la performance par endpoint"""
        return stats_df.groupby("Name").agg({
            "Average Response Time": "mean",
            "Median Response Time": "mean",
            "95%": "mean",
            "Failure Count": "sum",
            "Total Request Count": "sum"
        }).sort_values("Average Response Time", ascending=False)
        
    def plot_response_times(self, history_df: pd.DataFrame, output_file: str):
        """Génère un graphique des temps de réponse"""
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=history_df, x="Timestamp", y="Average Response Time", hue="Name")
        plt.title("Temps de réponse moyen par endpoint")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
        
    def plot_requests_per_second(self, history_df: pd.DataFrame, output_file: str):
        """Génère un graphique des requêtes par seconde"""
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=history_df, x="Timestamp", y="Total RPS")
        plt.title("Requêtes par seconde")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
        
    def analyze_failures(self, failures_df: pd.DataFrame) -> Dict:
        """Analyse les échecs"""
        if failures_df.empty:
            return {"total_failures": 0, "failure_types": {}}
            
        return {
            "total_failures": len(failures_df),
            "failure_types": failures_df["Error"].value_counts().to_dict()
        }
        
    def generate_report(self) -> str:
        """Génère un rapport d'analyse complet"""
        stats_df, history_df, failures_df = self.load_latest_results()
        
        # Analyse des performances
        perf_metrics = self.analyze_performance(stats_df)
        endpoint_metrics = self.analyze_endpoints(stats_df)
        failure_analysis = self.analyze_failures(failures_df)
        
        # Génération des graphiques
        plots_dir = self.report_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        self.plot_response_times(history_df, str(plots_dir / "response_times.png"))
        self.plot_requests_per_second(history_df, str(plots_dir / "requests_per_second.png"))
        
        # Création du rapport HTML
        report_template = """
        <html>
        <head>
            <title>Rapport d'analyse des tests de charge</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric { margin: 10px 0; }
                .warning { color: red; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                img { max-width: 100%; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>Rapport d'analyse des tests de charge</h1>
            <p>Date du test: {date}</p>
            
            <h2>Métriques globales</h2>
            <div class="metric">Requêtes totales: {total_requests}</div>
            <div class="metric">Temps de réponse moyen: {avg_response_time:.2f} ms</div>
            <div class="metric">Temps de réponse médian: {median_response_time:.2f} ms</div>
            <div class="metric">95ème percentile: {p95_response_time:.2f} ms</div>
            <div class="metric">Requêtes par seconde: {requests_per_second:.2f}</div>
            <div class="metric">Pourcentage d'échecs: {failures_percent:.2f}%</div>
            
            <h2>Performance par endpoint</h2>
            {endpoint_table}
            
            <h2>Analyse des échecs</h2>
            <div class="metric">Échecs totaux: {total_failures}</div>
            {failure_types}
            
            <h2>Graphiques</h2>
            <img src="plots/response_times.png" alt="Temps de réponse">
            <img src="plots/requests_per_second.png" alt="Requêtes par seconde">
        </body>
        </html>
        """
        
        # Formatage du rapport
        report_html = report_template.format(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_requests=perf_metrics["total_requests"],
            avg_response_time=perf_metrics["avg_response_time"],
            median_response_time=perf_metrics["median_response_time"],
            p95_response_time=perf_metrics["p95_response_time"],
            requests_per_second=perf_metrics["requests_per_second"],
            failures_percent=perf_metrics["failures_percent"],
            endpoint_table=endpoint_metrics.to_html(),
            total_failures=failure_analysis["total_failures"],
            failure_types="<br>".join([f"{k}: {v}" for k, v in failure_analysis["failure_types"].items()])
        )
        
        # Sauvegarde du rapport
        report_file = self.report_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_file.write_text(report_html)
        
        return str(report_file)

if __name__ == "__main__":
    analyzer = LoadTestAnalyzer("reports/load_tests")
    report_path = analyzer.generate_report()
    print(f"Rapport généré: {report_path}")
