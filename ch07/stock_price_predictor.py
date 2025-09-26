import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def load_processed_data(data_dir="processed_data"):
    try:
        train_files = glob.glob(f"{data_dir}/X_train_*.csv")
        test_files = glob.glob(f"{data_dir}/X_test_*.csv")
        y_train_files = glob.glob(f"{data_dir}/y_train_*.csv")
        y_test_files = glob.glob(f"{data_dir}/y_test_*.csv")

        if not train_files or not test_files:
            print(f"'{data_dir}' 폴더에서 전처리된 데이터 파일을 찾을 수 없습니다.")
            return None, None, None, None

        latest_train = max(train_files, key=os.path.getctime)
        latest_test = max(test_files, key=os.path.getctime)
        latest_y_train = max(y_train_files, key=os.path.getctime)
        latest_y_test = max(y_test_files, key=os.path.getctime)

        print("=== 데이터 로드 ===")
        print(f"훈련 특성 파일: {os.path.basename(latest_train)}")
        print(f"테스트 특성 파일: {os.path.basename(latest_test)}")
        print(f"훈련 타겟 파일: {os.path.basename(latest_y_train)}")
        print(f"테스트 타겟 파일: {os.path.basename(latest_y_test)}")

        X_train = pd.read_csv(latest_train, index_col=0)
        X_test = pd.read_csv(latest_test, index_col=0)
        y_train = pd.read_csv(latest_y_train, index_col=0).iloc[:, 0]
        y_test = pd.read_csv(latest_y_test, index_col=0).iloc[:, 0]

        print(f"훈련 데이터: {X_train.shape[0]}개 샘플, {X_train.shape[1]}개 특성")
        print(f"테스트 데이터: {X_test.shape[0]}개 샘플, {X_test.shape[1]}개 특성")

        return X_train, X_test, y_train, y_test

    except Exception as error:
        print(f"데이터 로드 중 오류 발생: {error}")
        return None, None, None, None


def clean_data(X_train, X_test, y_train, y_test):
    print("\n=== 데이터 정리 ===")
    print("무한대 값 확인:")
    for col in X_train.columns:
        inf_count = np.isinf(X_train[col]).sum()
        if inf_count > 0:
            print(f"  {col}: {inf_count}개")

    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.replace([np.inf, -np.inf], np.nan)

    for col in X_train.columns:
        if X_train[col].isnull().sum() > 0:
            median_val = X_train[col].median()
            X_train[col].fillna(median_val, inplace=True)
            X_test[col].fillna(median_val, inplace=True)

    print("이상치 제거:")
    for col in X_train.columns:
        mean_val = X_train[col].mean()
        std_val = X_train[col].std()
        lower_bound = mean_val - 3 * std_val
        upper_bound = mean_val + 3 * std_val
        outlier_count = ((X_train[col] < lower_bound) | (X_train[col] > upper_bound)).sum()
        if outlier_count > 0:
            print(f"  {col}: {outlier_count}개 이상치")
            median_val = X_train[col].median()
            X_train.loc[X_train[col] < lower_bound, col] = median_val
            X_train.loc[X_train[col] > upper_bound, col] = median_val

    print("데이터 정리 완료!")
    return X_train, X_test, y_train, y_test


def train_linear_regression_model(X_train, y_train):
    print("\n=== 선형 회귀 모델 훈련 ===")
    model = LinearRegression()
    model.fit(X_train, y_train)
    print("모델 훈련 완료!")
    print(f"절편 (Intercept): {model.intercept_:.2f}")
    feature_importance = pd.DataFrame({
        '특성': X_train.columns,
        '계수': model.coef_
    }).sort_values('계수', key=abs, ascending=False)
    print("\n=== 특성 중요도 (절댓값 기준) ===")
    for i, (_, row) in enumerate(feature_importance.head(10).iterrows(), 1):
        print(f"{i:2d}. {row['특성']:<20} : {row['계수']:>10.2f}")
    return model, feature_importance


def evaluate_model(model, X_test, y_test):
    print("\n=== 모델 성능 평가 ===")
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    print(f"평균 제곱 오차 (MSE): {mse:,.2f}")
    print(f"평균 제곱근 오차 (RMSE): {rmse:,.2f}")
    print(f"평균 절대 오차 (MAE): {mae:,.2f}")
    print(f"결정 계수 (R²): {r2:.4f}")
    print(f"평균 절대 오차 비율 (MAPE): {mape:.2f}%")
    return y_pred, {'mse': mse, 'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape}


def plot_predictions(y_test, y_pred, save_dir="results"):
    print("\n=== 예측 결과 시각화 ===")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # font_test.py 방식으로 한글 폰트 설정 (전역 설정)
    try:
        # font_test.py에서 사용한 방식과 동일하게 설정
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        print("✓ 한글 폰트 설정 완료: Malgun Gothic (font_test.py 방식)")
    except Exception as e:
        print(f"⚠️ 폰트 설정 실패: {e}")
        # 대체 폰트 시도
        try:
            plt.rcParams['font.family'] = 'Batang'
            plt.rcParams['axes.unicode_minus'] = False
            print("✓ 대체 폰트 설정: Batang")
        except:
            print("⚠️ 폰트 설정 실패")
    
    plt.rcParams['font.size'] = 10
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)

    # font_test.py와 동일한 방식으로 그래프 생성
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    axes[0, 0].scatter(y_test, y_pred, alpha=0.6, color='blue')
    axes[0, 0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[0, 0].set_xlabel('실제 주가')
    axes[0, 0].set_ylabel('예측 주가')
    axes[0, 0].set_title('실제값 vs 예측값')
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(y_test.index, y_test.values, label='실제', color='blue', alpha=0.7)
    axes[0, 1].plot(y_test.index, y_pred, label='예측', color='red', alpha=0.7)
    axes[0, 1].set_xlabel('날짜')
    axes[0, 1].set_ylabel('주가')
    axes[0, 1].set_title('시간에 따른 주가 예측')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    residuals = y_test - y_pred
    axes[1, 0].hist(residuals, bins=30, alpha=0.7, color='green', edgecolor='black')
    axes[1, 0].set_xlabel('예측 오차')
    axes[1, 0].set_ylabel('빈도수')
    axes[1, 0].set_title('예측 오차 분포')
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(y_test.index, residuals, color='orange', alpha=0.7)
    axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[1, 1].set_xlabel('날짜')
    axes[1, 1].set_ylabel('예측 오차')
    axes[1, 1].set_title('시간에 따른 예측 오차')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"{save_dir}/prediction_results_{timestamp}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"그래프가 저장되었습니다: {plot_filename}")
    plt.show()


def save_model_results(model, feature_importance, metrics, save_dir="results"):
    print("\n=== 결과 저장 ===")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # models 폴더 생성
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 특성 중요도와 성능 지표 저장
    feature_importance.to_csv(f"{save_dir}/feature_importance_{timestamp}.csv", index=False, encoding='utf-8-sig')
    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(f"{save_dir}/model_performance_{timestamp}.csv", index=False, encoding='utf-8-sig')
    
    # 훈련된 모델 저장 (pickle 형식)
    import pickle
    model_filename = f"{models_dir}/stock_price_model_{timestamp}.pkl"
    with open(model_filename, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"특성 중요도: {save_dir}/feature_importance_{timestamp}.csv")
    print(f"성능 지표: {save_dir}/model_performance_{timestamp}.csv")
    print(f"훈련된 모델: {model_filename}")


def predict_next_day(model, X_test, y_test, feature_names):
    print("\n=== 다음날 주가 예측 ===")
    latest_data = X_test.iloc[-1:].values
    next_day_prediction = model.predict(latest_data)[0]
    print(f"가장 최근 데이터 기준일: {X_test.index[-1]}")
    print(f"예측된 다음날 주가: {next_day_prediction:,.0f}원")
    confidence = "높음" if model.score(X_test, y_test) > 0.7 else "보통" if model.score(X_test, y_test) > 0.5 else "낮음"
    print(f"예측 신뢰도: {confidence}")
    return next_day_prediction


def main():
    print("=== 삼성전자 주가 예측 모델 (선형 회귀) ===")
    X_train, X_test, y_train, y_test = load_processed_data()
    if X_train is None:
        print("데이터 로드에 실패했습니다. 먼저 data_preprocessing.py를 실행해주세요.")
        return
    X_train, X_test, y_train, y_test = clean_data(X_train, X_test, y_train, y_test)
    model, feature_importance = train_linear_regression_model(X_train, y_train)
    y_pred, metrics = evaluate_model(model, X_test, y_test)
    plot_predictions(y_test, y_pred)
    save_model_results(model, feature_importance, metrics)
    predict_next_day(model, X_test, y_test, X_test.columns)
    print("\n=== 모델 훈련 완료 ===")
    print("📊 주요 결과:")
    print(f"  - 모델 정확도 (R²): {metrics['r2']:.4f}")
    print(f"  - 평균 예측 오차: {metrics['mae']:,.0f}원")
    print(f"  - 예측 오차 비율: {metrics['mape']:.2f}%")

if __name__ == "__main__":
    main()
