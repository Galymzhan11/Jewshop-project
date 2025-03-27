
document.addEventListener('DOMContentLoaded', function() {
  const background = document.getElementById('luxury-background');
  const starCount = 30;
  
  for (let i = 0; i < starCount; i++) {
    createStar(background);
  }
  
  // Периодически добавляем новые звезды
  setInterval(function() {
    createStar(background);
  }, 2000);
});

function createStar(container) {
  const star = document.createElement('div');
  star.classList.add('star');
  
  // Случайный размер звезды
  const size = Math.random() * 1.5 + 0.5;
  star.style.fontSize = `${size}em`;
  
  // Случайная позиция
  const posX = Math.random() * 100;
  const posY = Math.random() * 100;
  star.style.left = `${posX}%`;
  star.style.bottom = `${posY}%`;
  
  // Случайная длительность анимации
  const duration = Math.random() * 10 + 15;
  star.style.animationDuration = `${duration}s`;
  
  // Случайная задержка
  const delay = Math.random() * 10;
  star.style.animationDelay = `${delay}s`;
  
  container.appendChild(star);
  
  // Удаляем звезду после завершения анимации
  setTimeout(() => {
    star.remove();
  }, (duration + delay) * 1000);
}