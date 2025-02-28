import streamlit as st
import os
from FW_transfer import process_fw_transfer

def main():
    st.title("FW Transfer Application")
    
    # ファイルアップロード部分
    st.header("1. ファイルのアップロード")
    
    col1, col2 = st.columns(2)
    with col1:
        aws_file = st.file_uploader(
            "AWS通信要件ヒアリングシートをアップロード",
            type=["xlsx"],
            key="aws_file"
        )
    
    with col2:
        fw_file = st.file_uploader(
            "InternalFW_RuleListをアップロード",
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
                
                # 処理実行
                success, message, output_file = process_fw_transfer(temp_aws, temp_fw)
                
                if success:
                    progress_bar.progress(100)
                    status_text.text("処理完了！")
                    
                    # 結果ファイルの表示
                    if output_file and os.path.exists(output_file):
                        with open(output_file, 'rb') as f:
                            st.download_button(
                                label="結果をダウンロード",
                                data=f,
                                file_name="InternalFW_RuleList_Tokyo_Prod_final.xlsx",
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

if __name__ == "__main__":
    main() 