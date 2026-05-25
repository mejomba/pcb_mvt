const track = document.querySelector('.track');
const carousel = document.querySelector('.carousel');
const left = document.querySelector('.left');
const right = document.querySelector('.right');
const carouselWidth = carousel.offsetWidth;
let index = 0;
let sumOfRight = carouselWidth;
let sumOfLeft = 0;
let initialPosition = null;
let moving = false;
let transform = 0;
let lastPageX = 0;
let transformValue = 0;

const gestureStart =  (e) => {
   initialPosition = e.pageX;
   moving = true;
   const transformMatrix = window.getComputedStyle(track).getPropertyValue('transform');
   if (transformMatrix !== 'none') {
       transform = parseInt(transformMatrix.split(',')[4].trim());
   }
};

const gestureMove = (e) => {
    track.classList.remove('smooth-transition');
    if (moving) {
        const diff = e.pageX - initialPosition;
        if (e.pageX - lastPageX > 0) {
                sumOfRight = Math.abs(transformValue);
            if (transformValue > 0) {
                return;
            }
        } else {
                sumOfRight = Math.abs(transformValue);
            if (Math.abs(transformValue) > track.offsetWidth - carousel.offsetWidth ) {
                return;
            }
        }
        transformValue = parseInt(transform) + diff;
        track.style.transform = `translateX(${transformValue}px)`;
    }
    lastPageX = e.pageX;
    if (Math.abs(transformValue) > 10) {
    left.classList.add('show');
    }
    if (Math.abs(transformValue) <= track.offsetWidth) {
        right.classList.remove('lock');
    }
};

const gestureEnd =  () => {
    moving = false;
};

if (window.PointerEvent) {
    carousel.addEventListener('pointerdown', gestureStart);
    carousel.addEventListener('pointermove', gestureMove);
    carousel.addEventListener('pointerup',gestureEnd);
} else {
    carousel.addEventListener('touchdown', gestureStart);
    carousel.addEventListener('touchmove', gestureMove);
    carousel.addEventListener('touchup',gestureEnd);

    carousel.addEventListener('mousedown', gestureStart);
    carousel.addEventListener('mousemove', gestureMove);
    carousel.addEventListener('mouseup',gestureEnd);
}

right.addEventListener('click', function () {
    track.classList.add('smooth-transition');
    index++;
    left.classList.add('show');
    if ((sumOfRight + carouselWidth - (transformValue) ) < track.offsetWidth) {
        track.style.transform = track.style.transform + `translate(-${carouselWidth}px)`;
        sumOfRight = sumOfRight + carouselWidth;
    } else {
        track.style.transform = `translate(-${track.offsetWidth - carouselWidth}px)`;
        sumOfRight = track.offsetWidth;
    }
    if (sumOfRight === track.offsetWidth) {
        right.classList.add('lock');
    }
});
left.addEventListener('click', function () {
    track.classList.add('smooth-transition');
    sumOfLeft = sumOfRight - carouselWidth + transform;

    if ((Math.abs(sumOfRight) > carouselWidth)) {
        track.style.transform = track.style.transform + `translate(${carouselWidth}px)`;
        sumOfRight -= carouselWidth;
    } else {
        track.style.transform = `translate(-${0}px)`;
        sumOfRight = 0;
    }
    index--;
    right.classList.remove('lock');
    if (sumOfRight === carouselWidth || sumOfRight < 10) {
        left.classList.remove('show');
    }
});