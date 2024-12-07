// Include Swiper JS
const swiper = new Swiper('.swiper-container', {
    loop: true, // Enable looping
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    autoplay: {
        delay: 5000, // Autoplay delay
        disableOnInteraction: false,
    },
});

document.addEventListener('DOMContentLoaded', function () {
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    let maxHeight = 0;

    testimonialCards.forEach(card => {
        const cardHeight = card.offsetHeight;
        if (cardHeight > maxHeight) {
            maxHeight = cardHeight;
        }
    });

    testimonialCards.forEach(card => {
        card.style.height = maxHeight + 'px';
    });

    var testimonialCarousel = new bootstrap.Carousel(document.getElementById('testimonialCarousel'), {
        interval: 5000,
        wrap: true,
        keyboard: true
    });

    // Smooth Scroll functionality
    document.querySelectorAll('.nav-item a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const target = document.querySelector(this.getAttribute('href'));

            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    });
});