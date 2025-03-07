import streamlit as st
import os
from FW_transfer import process_fw_transfer

def main():
    st.title("FW Transfer Application")
    
    # リージョンと環境の選択
    st.header("環境設定")
    col1, col2 = st.columns(2)
    
    with col1:
        region = st.selectbox(
            "リージョンを選択",
            options=["tokyo", "singapore", "virginia"],
            index=0
        )
    
    with col2:
        environment = st.selectbox(
            "環境を選択",
            options=["prod", "nonprod"],
            index=0
        )
    
    # 環境変数からデフォルト値を取得（Kubernetes環境用）
    region = os.environ.get("REGION", region)
    environment = os.environ.get("ENVIRONMENT", environment)
    
    # ファイルアップロード部分
    st.header("ファイルのアップロード")
    
    env_suffix = "Prod" if environment.lower() == "prod" else "NonProd"
    
    col1, col2 = st.columns(2)
    with col1:
        aws_file = st.file_uploader(
            "AWS通信要件ヒアリングシートをアップロード",
            type=["xlsx"],
            key="aws_file"
        )
    
    with col2:
        fw_file = st.file_uploader(
            f"InternalFW_RuleList_{region.capitalize()}_{env_suffix}をアップロード",
            type=["xlsx"],
            key="fw_file"
        )

    # 処理実行ボタン
    if st.button("処理開始", disabled=not (aws_file and fw_file)):
        if aws_file and fw_file:
            # プログレスバーの表示
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 一時ファイルとして保存
            temp_aws = f"temp_aws_{aws_file.name}"
            temp_fw = f"temp_fw_{fw_file.name}"
            
            try:
                # アップロードされたファイルを一時保存
                with open(temp_aws, 'wb') as f:
                    f.write(aws_file.getvalue())
                with open(temp_fw, 'wb') as f:
                    f.write(fw_file.getvalue())
                
                # 進捗表示
                status_text.text("処理中...")
                progress_bar.progress(50)
                
                # 処理実行（リージョンと環境を指定）
                success, message, output_file = process_fw_transfer(
                    temp_aws, temp_fw, region=region, environment=environment
                )
                
                if success:
                    progress_bar.progress(100)
                    status_text.text("処理完了！")
                    
                    # 結果ファイルの表示
                    if output_file and os.path.exists(output_file):
                        with open(output_file, 'rb') as f:
                            output_filename = os.path.basename(output_file)
                            st.download_button(
                                label="結果をダウンロード",
                                data=f,
                                file_name=output_filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                else:
                    st.error(message)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
            
            finally:
                # 一時ファイルの削除
                if os.path.exists(temp_aws):
                    os.remove(temp_aws)
                if os.path.exists(temp_fw):
                    os.remove(temp_fw)

    # 使用方法の説明
    with st.expander("使用方法"):
        st.markdown("""
        ### 使用方法
        1. リージョンと環境を選択します
        2. AWS通信要件ヒアリングシートをアップロードします
        3. 対応するInternalFW_RuleListファイルをアップロードします
        4. 「処理開始」ボタンをクリックします
        5. 処理が完了したら、結果ファイルをダウンロードします
        
        ### 対応リージョン・環境
        - リージョン: 東京、シンガポール、バージニア
        - 環境: 本番(Prod)、非本番(NonProd)
        """)

if __name__ == "__main__":
    main() 