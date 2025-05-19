let currentPage = 1;
const imagesPerPage = 10;
const tbody = document.getElementById("imagesTableBody");

const imagesContainer = document.getElementById("images-placeholder");

function setImages(images) {
  images.forEach((image) => {
    const tr = document.createElement("tr");
    const tdPreview = document.createElement("td");
    const tdUrl = document.createElement("td");
    const tdSize = document.createElement("td");
    const tdTime = document.createElement("td");
    const tdDelete = document.createElement("td");
    const deleteBtn = document.createElement("button");

    const fullFileName = image.filename + image.file_type;

    deleteBtn.onclick = () => {
      fetch(`/api/delete/${fullFileName}`, { method: "DELETE" })
        .then(() => loadImages(currentPage))
        .catch((error) => console.error(error));
    };

    deleteBtn.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16"> <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/></svg>';
    deleteBtn.classList.add("delete-btn");

    tdDelete.appendChild(deleteBtn);

    tdPreview.innerHTML = `<img src="/images/${fullFileName}" width="42" height="100%">`;
    tdUrl.innerHTML = `<a href="/images/${fullFileName}" target="_blank">${image.original_filename}${image.file_type}</a>`;
    tdSize.innerHTML = image.size;
    tdTime.innerHTML = image.upload_date;

    tr.appendChild(tdPreview);
    tr.appendChild(tdUrl);
    tr.appendChild(tdSize);
    tr.appendChild(tdTime);
    tr.appendChild(tdDelete);

    tbody.appendChild(tr);
  });
}

function loadImages(page) {
  fetch(`/api/images-list/?page=${page}`)
    .then((response) => response.json())
    .then((data) => {
      tbody.innerHTML = "";
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

loadImages(1);