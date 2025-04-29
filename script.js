async function uploadImage() {
    const fileInput = document.getElementById('upload');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select an image file first!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch('http://127.0.0.1:8000/blur/', {
        method: 'POST',
        body: formData,
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        document.getElementById('result').src = url;
    } else {
        alert("Face blur failed!");
    }
}
