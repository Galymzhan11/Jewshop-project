// Функция для инициализации навбара
document.addEventListener('DOMContentLoaded', function() {
  // Обработчики для выпадающих меню в десктопной версии
  initDropdowns();
  
  // Обработчики для мобильной навигации
  initMobileMenu();
  
  // Обработчики для мобильных выпадающих меню
  initMobileDropdowns();
});

// Инициализация выпадающих меню
function initDropdowns() {
  const dropdowns = document.querySelectorAll('.dropdown');
  
  // Обработка клика по кнопке выпадающего меню
  dropdowns.forEach(dropdown => {
    const button = dropdown.querySelector('.dropdown-toggle');
    
    button.addEventListener('click', function(e) {
      e.stopPropagation();
      
      // Закрываем все другие выпадающие меню
      dropdowns.forEach(otherDropdown => {
        if (otherDropdown !== dropdown) {
          otherDropdown.classList.remove('active');
        }
      });
      
      // Переключаем активное состояние текущего меню
      dropdown.classList.toggle('active');
    });
  });
  
  // Закрытие выпадающих меню при клике вне меню
  document.addEventListener('click', function(e) {
    dropdowns.forEach(dropdown => {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('active');
      }
    });
  });
}

// Инициализация мобильного меню
function initMobileMenu() {
  const mobileToggle = document.querySelector('.mobile-menu-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', function() {
      mobileMenu.classList.toggle('active');
      
      // Анимация иконки бургер-меню
      this.classList.toggle('active');
      
      // Запрет прокрутки страницы при открытом меню
      if (mobileMenu.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    });
  }
}

// Инициализация выпадающих меню в мобильной версии
function initMobileDropdowns() {
  const mobileDropdowns = document.querySelectorAll('.mobile-dropdown');
  
  mobileDropdowns.forEach(dropdown => {
    const button = dropdown.querySelector('.mobile-dropdown-toggle');
    
    if (button) {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Переключаем активное состояние
        dropdown.classList.toggle('active');
      });
    }
  });
}

// Обновление состояния выпадающих меню при изменении размера окна
window.addEventListener('resize', function() {
  const mobileMenu = document.querySelector('.mobile-menu');
  
  if (window.innerWidth > 991 && mobileMenu && mobileMenu.classList.contains('active')) {
    mobileMenu.classList.remove('active');
    document.body.style.overflow = '';
    
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileToggle) {
      mobileToggle.classList.remove('active');
    }
  }
}); 