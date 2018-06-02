var form = document.getElementById('document-form'),
    file = document.getElementById('file');
function isPdf(elem) {
    var val = elem.value.toLowerCase()
    return val.endsWith('.pdf');
}
function indicate_error() {
    document.getElementById('help').classList.add('is-danger');
    document.getElementById('file-container').classList.add('is-danger');
}
function remove_error() {
    document.getElementById('help').classList.remove('is-danger');
    document.getElementById('file-container').classList.remove('is-danger');
}

file.onchange = function (e) {
    var filename = document.getElementById('file-name');
    if (file.files.length > 0) {
        filename.innerHTML = file.files[0].name;
        if (!isPdf(file)) {
            indicate_error();
        }
        else
            remove_error();
    }
    else {
        file.value = '';
        filename.innerHTML = ''
    }
}

form.onsubmit = function (e) {
    e.preventDefault();
    if (isPdf(file))
        form.submit();
    else
        indicate_error()
}
