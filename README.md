![ScheduleFlowBot](https://b.radikal.ru/b20/1910/3d/7268401b5e3c.png)
____
### __Программа для загрузки расписания с сайта амтэк35.рф и дальнейшей его обработки.__
Дилетантский проект на питоне, задача которого облегчить доступ к расписанию АМТЭКа.
___  

ChangeLog:  
__1.0B - 3 октября'19:__
- На основе ScheduleFlow начата разработка бота на платформе ВКонтакте.

__1.0.1B - 4 октября'19:__
- Небольшие дополнения. Повышение стабильности.

__1.2 - 2 октября'19:__  
- Добавлена функция crop_for_class, позволяющая искать класс в ограниченном диапазоне
- Сохранение расписания в папку (независимо от того, нужен отдельный класс или все)
- При использовании параметра 'all' в консоль выводятся номера классов

__1.2.1 - 6 октября'19:__
- Небольшие изменения, связаные, по большей части с ScheduleFlowBot

__1.1B - 6 октября'19:__
- Заложен функционал для реализации команд.
- Добавлена опция выбора даты.
- Повышена отказоустойчивость.

__1.3.4B - 9 октября'19:__
- Реализованы все функции
- Стабильная работа на сервере

__1.3 - 9 октября'19:__
- ScheduleFlowBot переходит в ветку master, т.к. консольная версия больше никому не нужна

__1.4 - 10 октября'19:__
- UX 2.0. Работа осуществляется по большей части с помощью кнопок.

__1.4.5 - 10 октября'19:__
- Переделана функция, возвращающая дату
- Убраны баги
- Бот отправляет смайлики :) 

__1.4.6 - 14 октября'19:__
- Исправления багов

__1.4.7 - 17 октября'19:__
- Переделан внешний вид присылаемого расписания
- Добавлено расписание звонков
- Исправлен баг с множественным выбором класса
- Добавлен трекер состояния пользователя

__1.4.8 - 19 октября'19:__
- Минорные исправления
- Исправлено расписание звонков

__1.5 - 25 октября - ноябрь'19:__
- Расписание загружается на сервер прямо при нарезке
- Время отправки расписания снижено в несколько раз
- Снижен объем хранящихся данных засчет того, что хранятся только
  attachments и основное расписание (возможно отключить через параметр в
  Constantes)
- Бот "набирает сообщение"
- Если сообщение не является командой, бот ответит на него емким
  высказываением, либо просто прочитает
- Обработка стикеров, картинок, аудио
- Возможность отвечать через интерфейс консоли
- При запросе расширенной статистики отправляется гистограмма по
  пользователям
- Рассылка расписания пользователям одной командой
- Возможность включить и выключить "подписку" на расписание
- Небольшая утилита для работы с базой пользователей UserBase