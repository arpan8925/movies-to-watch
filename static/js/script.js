'use strict';

const carouselItems = document.querySelectorAll('.carousel__item');
let currentItem = document.querySelector('.carousel__item--main');
const leftBtn = document.querySelector('#leftBtn');
const rightBtn = document.querySelector('#rightBtn');

function updateCarouselClasses() {
    carouselItems.forEach((item, i) => {
        item.classList.remove('carousel__item--left', 'carousel__item--main', 'carousel__item--right');
    });

    const currentId = Array.from(carouselItems).indexOf(currentItem);

    const leftItem = currentId === 0 ? carouselItems[carouselItems.length - 1] : carouselItems[currentId - 1];
    const rightItem = currentId === carouselItems.length - 1 ? carouselItems[0] : carouselItems[currentId + 1];

    leftItem.classList.add('carousel__item--left');
    currentItem.classList.add('carousel__item--main');
    rightItem.classList.add('carousel__item--right');
}

rightBtn.addEventListener('click', function () {
    currentItem = document.querySelector('.carousel__item--right');
    updateCarouselClasses();
});

leftBtn.addEventListener('click', function () {
    currentItem = document.querySelector('.carousel__item--left');
    updateCarouselClasses();
});
