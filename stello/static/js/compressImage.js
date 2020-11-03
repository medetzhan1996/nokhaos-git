function compressImage(event, useWebWorker) {
    var file = event.target.files[0]
    var progressDom
    if (useWebWorker) {
        progressDom = document.querySelector('#web-worker-progress')
    }
    else {
        progressDom = document.querySelector('#main-thread-progress')
    }
    // console.log('input', file)
    imageCompression.getExifOrientation(file).then(function (o) {
        // console.log('ExifOrientation', o)
    })

    var options = {
        maxSizeMB: 1,
        maxWidthOrHeight: parseFloat(1920),
        useWebWorker: false,
        onProgress: onProgress
    }
    imageCompression(file, options).then(function (output) {
        const downloadLink = URL.createObjectURL(output)
        document.getElementById('preview-after-compress').src = downloadLink
        $('.photo').removeClass('d-none')
        var reader = new FileReader();
        reader.readAsDataURL(output); 
        reader.onloadend = function() {
            var base64data = reader.result;                
            $('#photo-base64').val(base64data)
        }
    })
    

    function onProgress (p) {
        progressDom.innerHTML = '(' + p + '%' + ')'
    }
}