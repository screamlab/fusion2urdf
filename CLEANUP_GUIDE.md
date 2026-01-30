# URDF 匯出後自動清理指南

## 問題說明

在使用 fusion2urdf 工具將 Fusion 360 模型轉換為 URDF 檔案時，系統會執行以下步驟：

1. 複製原始元件來準備 STL 匯出
2. 將原始元件重新命名為 'old_component'
3. 為複製的元件建立 STL 檔案
4. 產生 URDF 和相關檔案

**問題：** 在步驟完成後，這些複製的元件和重新命名的元件會留在原始 Fusion 360 檔案中，造成：
- 檔案結構混亂
- 元件樹冗餘
- 檔案大小增加
- 後續編輯困難

## 解決方案

### 1. 自動清理功能（推薦）

**新功能：** 在 URDF 匯出過程中自動清理複製的元件

**使用方法：**
1. 執行 `URDF_Exporter` 腳本
2. 選擇儲存目錄後，會出現詢問對話框：
   ```
   Do you want to automatically clean up copied components after URDF generation?
   
   YES: Clean up (recommended) - removes temporary components created during export
   NO: Keep components - temporary components will remain in your Fusion file
   ```
3. 選擇 "YES"（建議）進行自動清理

**清理過程：**
- 移除所有為 STL 匯出而建立的複製元件
- 還原原始元件的名稱（從 'old_component' 還原為原始名稱）
- 提供清理狀態的反饋訊息

### 2. 手動清理工具

**適用情況：** 如果您之前產生 URDF 時選擇保留複製元件，或需要清理舊的複製元件

**使用方法：**
1. 在 Fusion 360 中執行 `cleanup_components` 腳本
2. 腳本會自動偵測：
   - 複製的元件（包含 'copy', 'temp_', 'duplicate' 等關鍵字）
   - 重新命名的原始元件（名稱為 'old_component'）
3. 確認清理操作後，腳本會自動執行清理

## 清理邏輯

### 識別複製元件
```python
# 辨識需要移除的複製元件
- 元件名稱不包含 'old_component'
- 在 STL 匯出過程中新建立的元件

# 辨識需要還原的原始元件  
- 元件名稱為 'old_component'
- 原本的元件被重新命名
```

### 清理步驟
1. **移除複製元件：** 
   - 以反向順序刪除，避免索引問題
   - 包含錯誤處理，確保清理失敗不影響主要功能

2. **還原原始名稱：**
   - base_link 元件還原為 'base_link'
   - 其他元件根據 occurrence 名稱還原
   - 移除特殊字元並格式化名稱

## 錯誤處理

### 自動清理錯誤
- 如果清理失敗，會顯示警告訊息但不影響 URDF 產生
- 錯誤訊息會包含在最終的成功對話框中

### 手動清理錯誤
- 提供詳細的錯誤追蹤訊息
- 個別元件清理失敗不會中止整個清理過程

## 最佳實踐建議

1. **建議使用自動清理：** 選擇 "YES" 來自動清理複製元件
2. **定期清理：** 如果忘記使用自動清理，定期執行手動清理工具
3. **備份重要檔案：** 在進行大量 URDF 匯出前備份重要的 Fusion 360 檔案
4. **檢查清理結果：** 清理完成後檢查元件樹確認清理效果

## 故障排除

### 常見問題

**Q: 清理後元件名稱不正確**
A: 這通常是因為原始 occurrence 名稱包含特殊字元。清理工具會自動處理大部分情況，但複雜名稱可能需要手動調整。

**Q: 某些元件無法刪除**
A: 可能是因為元件被其他功能或約束參照。檢查 Fusion 360 的歷史記錄和約束設定。

**Q: 清理功能沒有執行**
A: 確認您選擇了 "YES" 進行自動清理，並檢查是否有錯誤訊息。

### 手動恢復
如果自動清理出現問題，您可以：
1. 使用 Fusion 360 的復原功能（Ctrl+Z）
2. 手動刪除不需要的複製元件
3. 手動重新命名 'old_component' 元件

## 技術細節

### 修改的檔案
- `URDF_Exporter.py`: 主要匯出腳本，新增清理選項和呼叫
- `utils/utils.py`: 新增 `cleanup_copied_components()` 函數
- `cleanup_components.py`: 獨立的清理工具腳本

### 關鍵函數
```python
def cleanup_copied_components(root):
    """
    移除在 STL 匯出過程中建立的複製元件
    """
    # 識別和移除複製元件
    # 還原原始元件名稱
    # 錯誤處理和日誌記錄
```

這個改進大幅提升了 fusion2urdf 工具的使用體驗，避免了原始檔案中累積不必要的複製元件。
