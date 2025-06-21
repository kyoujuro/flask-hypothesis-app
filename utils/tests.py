from scipy import stats
import pandas as pd

TEST_DESCRIPTIONS = {
    "t_test": "2群の平均値の差を検定。正規分布が前提。",
    "mann_whitney": "2群の中央値の差。非正規分布で使える。",
    "anova": "3群以上の平均値の差。",
    "kruskal": "3群以上の中央値の差。非正規分布で使える。",
    "chi2": "カテゴリデータの独立性を検定（クロス表）。",
    "fisher": "2x2クロス表での検定。小サンプル向き。",
    "shapiro": "データが正規分布かを検定。",
    "levene": "等分散性の検定（ANOVAの前提確認など）。"
}

def run_test(df, test_type, col1, col2=None):
    try:
        if test_type == "t_test":
            return stats.ttest_ind(df[col1], df[col2], nan_policy='omit')
        elif test_type == "mann_whitney":
            return stats.mannwhitneyu(df[col1], df[col2])
        elif test_type == "anova":
            groups = [group[col1].dropna() for _, group in df.groupby(col2)]
            return stats.f_oneway(*groups)
        elif test_type == "kruskal":
            groups = [group[col1].dropna() for _, group in df.groupby(col2)]
            return stats.kruskal(*groups)
        elif test_type == "chi2":
            table = pd.crosstab(df[col1], df[col2])
            return stats.chi2_contingency(table)
        elif test_type == "fisher":
            table = pd.crosstab(df[col1], df[col2])
            return stats.fisher_exact(table.values)
        elif test_type == "shapiro":
            return stats.shapiro(df[col1].dropna())
        elif test_type == "levene":
            groups = [group[col1].dropna() for _, group in df.groupby(col2)]
            return stats.levene(*groups)
        else:
            return "未対応の検定です"
    except Exception as e:
        return f"エラー: {str(e)}"
