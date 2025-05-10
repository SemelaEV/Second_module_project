const input = document.querySelector(".input");
const preview = document.querySelector(".preview");
const loadBtn = document.getElementById("loadBtn");

input.addEventListener("change", updateImagePreview);
loadBtn.addEventListener("click", () => {
  uploadFile();
});

loadBtn.disabled = true;

function updateImagePreview() {
    while (preview.firstChild) {
    preview.removeChild(preview.firstChild);
}

    const curFile = input.files[0];

    if (!curFile) {
        let textEl = document.createElement("p");
        extEl.textContent("Не выбран файл для загрузки");
        preview.appendChild(textEl);
    } else {
        const prevDivEl = document.createElement("div");
        preview.appendChild(prevDivEl);

        let filenamePEl = document.createElement("p");
        filenamePEl.className = "mb-0";
        filenamePEl.id = "filename";

        let fileSizePEl = document.createElement("p");

    if (checkFileType(curFile)) {
        loadBtn.disabled = false;
        filenamePEl.textContent = `Имя: ${curFile.name}`;
        fileSizePEl.textContent = `Размер: ${calcFileSize(curFile.size)}`;

        const imageEl = document.createElement("img");
        imageEl.id = "previewImage";
        imageEl.src = window.URL.createObjectURL(curFile);
        imageEl.style.width = "100%";
        imageEl.style.height = "auto";

        prevDivEl.appendChild(imageEl);
        prevDivEl.appendChild(filenamePEl);
        prevDivEl.appendChild(fileSizePEl);
    } else {
        filenamePEl.textContent = `Имя: ${curFile.name}`;
        fileSizePEl.textContent = "Неверный тип файла. Выберите другой.";
        prevDivEl.appendChild(filenamePEl);
        prevDivEl.appendChild(fileSizePEl);
        loadBtn.disabled = true;
    }
  }
}

function uploadFile() {
    const curFile = input.files[0];
    if (!File) return alert("Выберите файл для загрузки");

    fetch("/upload/", {
    method: "POST",
    headers: {
      Filename: curFile.name,
    },
    body: curFile,
  })
    .then((response) => {
      loadBtn.textContent = "Файл загружен успешно";
      loadBtn.disabled = true;

      fileLocation = response.headers.get("Location");
      fileName = response.headers.get("Filename");

      document.getElementById("filename").textContent = fileName;

      const downBtn = document.getElementById("downBtn");
      downBtn.hidden = false;
      downBtn.onclick = () => {
        const link = document.createElement("a");
        link.href = `images/${fileName}`;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      };

      const copyBtn = document.getElementById("copyBtn");
      copyBtn.hidden = false;
      copyBtn.onclick = () => {
        navigator.clipboard
          .writeText(fileLocation + fileName)
          .then(() => {
            alert("Ссылка скопирована в буфер обмена");
          })
          .catch((err) => {
            alert("Ошибка при копировании ссылки" + err);
          });
      };
    })
    .catch((err) => {
      console.error("Ошибка загрузки файла:", err);
    });
}

const fileTypes = ["image/jpeg", "image/jpg", "image/gif", "image/png"];

function checkFileType(file) {
    return fileTypes.includes(file.type);
}

function calcFileSize(fileSize) {
    if (fileSize < 1024) {
        return fileSize + " байт";
      } else if (fileSize > 1024 && fileSize < 1048576) {
        return (fileSize / 1024).toFixed(1) + " КБайт";
      } else if (fileSize > 1048576) {
        return (fileSize / 1048576).toFixed(1) + " МБайт";
      }
}