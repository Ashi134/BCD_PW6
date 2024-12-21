function get_prediction() {
    alert("in get prediction");
    const formData = new FormData()
    formData.append('image', image);
    console.log("get_prediction");
    fetch("/predict", {
        method: "POST",
        body: formData
    })
    .then(response => {
        alert(response);
        console.log(response);
        response.json().then(data => {

            const class_predicted = "malignant"
            const confidence = "0.8997134";
            // const class_predicted = "Begnig"
            // const confidence = "0.889312";
            // const class_predicted = "Non-cancerous"
            // const confidence = "NIL";

            loadingGif.style.display = "none";
            imageClass.innerHTML = `Class:${class_predicted}`;
            imageConfidence.innerHTML = `Confidence: ${confidence}`;
        });
    })
    .catch(error => {
        console.log("There was an error");
    });   
}

function imageUploaded(event) {
    const target = event.target;
    image = target.files[0];

    if (!image) return;

    imageClass.innerHTML = "";
    imageConfidence.innerHTML = "";
    loadingGif.style.display = "block";
    imageContainer.src = window.URL.createObjectURL(image);

    get_prediction(image);
}

function ready() {
    imageClass = document.querySelector("#imageClass");
    imageConfidence = document.querySelector("#imageConfidence");
    imageContainer = document.querySelector("#imageContainer");
    loadingGif = document.querySelector("#loadingGif");
    generatebutton = document.querySelector("#generatebutton");

    const inputFile = document.querySelector("#image");
    alert("in input file");
    generatebutton.addEventListener('click', get_prediction);
    inputFile.addEventListener('change', imageUploaded);

}

document.addEventListener("DOMContentLoaded", ready);

let imageContainer;
let imageClass;
let imageConfidence;
let loadingGif;
let image;