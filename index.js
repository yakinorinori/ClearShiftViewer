const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');  // pathモジュールのインポート
const app = express();
const port = 3000;
const multer = require('multer');

// multerのstorage設定をカスタマイズ
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'shiftPDF/'); // 保存先ディレクトリ
    },
    filename: function (req, file, cb) {
        // オリジナルのファイル名を使用（日付の追加を除去）
        cb(null, file.originalname);
    }
});

const upload = multer({ storage: storage });
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/form.html');
});

app.post('/runscript', (req, res) => {
    const employeeNumber = req.body.employeeNumber;
    const name = req.body.name;
    const startDate = req.body.startDate;
    const endDate = req.body.endDate;

    exec(`python3 shift.py "shiftPDF" "${employeeNumber}" "${name}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return res.send(`Error: ${error}`);
        }

        fs.readFile('sorted_output.csv', 'utf8', (err, data) => {
            if (err) {
                console.error(`readFile error: ${err}`);
                return res.send(`Error: ${err}`);
            }

            const filteredData = filterCsvData(data, startDate, endDate);

            // filtered_output.csv に保存
            fs.writeFile('filtered_output.csv', filteredData, (err) => {
                if (err) {
                    console.error(`writeFile error: ${err}`);
                    return res.send(`Error: ${err}`);
                }

                // HTMLファイルの更新
                let html = fs.readFileSync('public/results.html', 'utf8');
                const dynamicContent = `
                    <!-- DynamicContentStart -->
                    <div class="container">
                        <h1>シフト検索結果</h1>
                        <table>${convertCsvToHtmlTable(filteredData)}</table>
                    </div>
                    <!-- DynamicContentEnd -->
                `;
                html = html.replace(/<!-- DynamicContentStart -->([\s\S]*?)<!-- DynamicContentEnd -->/, dynamicContent);
                fs.writeFileSync('public/results.html', html);

                res.redirect('/results');
            });
        });
    });
});

app.get('/results', (req, res) => {
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.sendFile(path.join(__dirname, '/public/results.html'));
});

function filterCsvData(csvData, startDate, endDate) {
    const lines = csvData.split('\n');
    const filteredLines = lines.filter(line => {
        const dateMatch = line.match(/^\d{4}\/\d{2}\/\d{2}/);
        if (!dateMatch) return false;

        const dateStr = dateMatch[0];
        const date = new Date(dateStr);
        return date >= new Date(startDate) && date <= new Date(endDate);
    });

    return filteredLines.join('\n');
}
function convertCsvToHtmlTable(csvData) {
    const rows = csvData.split('\n');
    let table = '<table><tr><th>日付</th><th>出勤時間</th><th>退勤時間</th><th>勤務時間</th><th>休憩時間</th></tr>';

    rows.forEach(row => {
        const columns = row.split(',');
        table += '<tr>';
        columns.forEach(column => {
            table += `<td>${column}</td>`;
        });
        table += '</tr>';
    });

    table += '</table>';
    return table;
}

app.use(bodyParser.json()); // JSONの解析を有効化

app.post('/saveToCalendar', (req, res) => {
    const colorId = req.body.color; // リクエストボディから色IDを取得
    exec(`python3 event.py ${colorId}`, (error, stdout, stderr) => { // 色IDを引数として渡す
        if (error) {
            console.error(`exec error: ${error}`);
            return res.send(`Error: ${error}`);
        }
        res.send('カレンダに保存されました');
    });
});
// ファイルアップロードのルート
app.post('/upload', upload.single('file'), (req, res) => {
    const file = req.file;
    if (!file) {
        return res.status(400).send('ファイルがアップロードされませんでした。');
    }
    console.log(`アップロードされたファイル: ${file.path}`);
    res.send('ファイルがアップロードされました。');
});



app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
