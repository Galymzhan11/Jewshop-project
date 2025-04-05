function changeImage(src, thumbnail) {
    document.getElementById('main-image').src = src;
    
    // Remove selected class from all thumbnails
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    thumbnails.forEach(item => {
        item.classList.remove('selected');
    });
    
    // Add selected class to clicked thumbnail
    thumbnail.classList.add('selected');
}