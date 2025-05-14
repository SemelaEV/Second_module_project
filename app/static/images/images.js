let currentPage = 1;
const imagesPerPage = 9;

const closeBtn = document.getElementById("close");
const imagesContainer = document.getElementById("images-placeholder");

function setImages(images) {
  const modal = document.getElementById("modal");
  const modalImg = document.getElementById("modal-img");

  images.forEach((image) => {
    const fullImageName = image.filename + image.file_type;
    const mainDivEl = document.createElement("div");
    mainDivEl.className = "col m-2 rounded";
    mainDivEl.style.width = "310px";
    mainDivEl.style.height = "200px";
    imagesContainer.appendChild(mainDivEl);

    const imageDivElement = document.createElement("div");
    imageDivElement.className = "col m-2 rounded";
    imageDivElement.style.width = "300px";
    imageDivElement.style.height = "170px";
    mainDivEl.appendChild(imageDivElement);

    const imageElement = document.createElement("img");
    imageElement.src = `/images/${fullImageName}`;
    imageElement.alt = "Image";
    imageElement.style.height = "100%";
    imageElement.style.width = "auto";
    imageElement.addEventListener("click", () => {
      modalImg.src = `/images/${fullImageName}`;
      modal.style.display = "block";
    });

    imageDivElement.appendChild(imageElement);

    const buttonDivEl = document.createElement("div");
    buttonDivEl.className = "col m-2 rounded";
    buttonDivEl.style.width = "310px";
    buttonDivEl.style.height = "30px";
    mainDivEl.appendChild(buttonDivEl);

    const btnCopyLink = document.createElement("button");
    btnCopyLink.textContent = "Скопировать ссылку";
    btnCopyLink.className = "btn btn-secondary me-2 btn-sm px-2";
    btnCopyLink.onclick = () => {
      navigator.clipboard
        .writeText(window.location.origin + "/images/" + fullImageName)
        .then(() => {
          alert("Ссылка скопирована!");
        })
        .catch((err) => {
          alert("Ошибка при копировании ссылки: " + err);
        });
    };

    const btnDownload = document.createElement("button");
    btnDownload.textContent = "Загрузить";
    btnDownload.className = "btn btn-secondary me-2 btn-sm px-2";
    btnDownload.onclick = () => {
      const link = document.createElement("a");
      link.href = `/images/${fullImageName}`;
      link.download = fullImageName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };

    buttonDivEl.appendChild(btnCopyLink);
    buttonDivEl.appendChild(btnDownload);
  });
}

function loadImages(page) {
  fetch(`/api/images/?page=${page}`)
    .then((response) => response.json())
    .then((data) => {
      imagesContainer.innerHTML = "";
      if (data.images.length == 0) {
        const notImagesText = document.createElement("h2");
        notImagesText.textContent = "Нет загруженных изображений";
        imagesContainer.appendChild(notImagesText);
      } else {
        setImages(data.images);
        document.getElementById("nextPage").disabled =
          data.images.length < imagesPerPage;
        document.getElementById("prevPage").disabled = page === 1;
        document.getElementById("currentPage").textContent = page;
        currentPage = page;
      }
    });
}

document.getElementById("prevPage").addEventListener("click", () => {
  if (currentPage > 1) {
    loadImages(currentPage - 1);
  }
});

document.getElementById("nextPage").addEventListener("click", () => {
  loadImages(currentPage + 1);
});

closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

modal.addEventListener("click", () => {
  modal.style.display = "none";
});

loadImages(1);