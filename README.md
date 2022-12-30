# vlive_video_download

## 注意
未做太多防呆  
若在半途中突然關閉或是發生狀況請將最後下載且未完成的資料夾整個刪除後再重啟  
**請確保所有步驟跟網址格式都沒有問題**  
也請務必在空間足夠的硬碟中執行，謝謝  
若檔案下載完後將檔案移出程式的資料夾內將會判定為未下載過，請理解

## 開始
### 第一步
蒐集您想要下載的影片全部逐行放入`downloadurl.txt`中，請一個網址一行  
如果是想要在**搜尋欄位**的所有影片請這樣做
1. 請確保所有影片都load完成(拉到最底)  
2. F12 > Console  
3. 貼上這段後按下enter，將內容貼到程式資料夾內的`downloadurl.txt`中
 ```js
const dc = document.querySelectorAll("#content > div.search_result > div > div.inner > ul > li:nth-child(n) > a.video_tit")
let textarr = [];
for( i = 0; i<dc.length; i++) textarr.push(dc[i].href)
let results = '';
textarr.forEach((str, index) => {
  if (index > 0) {
    results += '\n';
  }
  results += str;
});
const blob = new Blob([results], { type: 'text/plain' });
const url = URL.createObjectURL(blob);
const link = document.createElement('a');
link.href = url;
link.download = 'downloadurl.txt';
document.body.appendChild(link);
link.click();
 ```
* 如果想要在搜尋的地方排除一些頻道，請在做2之前先執行這一段  
> ```js
> setInterval(fnc, 1000);
> 
> function fnc(){
>   var items = document.querySelectorAll("#content > div.search_result > div > div.inner > ul > li:nth-child(n) > div.video_date > a[href='你頻道的連結']");
> 
>   for (var i = 0; i < items.length; i++) {
>     var item = items[i];
>     var parent = item.parentNode.parentNode;
>     parent.remove();
>   }
> }
> ```

### 第二步  
將`requirememts.txt`的所需modules都先pip install裝好
```py
pip install -r requirements.txt
```
之後就可以執行`run.py`了
```py
python run.py
```
