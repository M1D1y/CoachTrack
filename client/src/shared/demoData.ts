import type { Athlete, Training } from '../entities/types'

export const trainer = { id: 100, name: 'Алексей Смирнов', sport: 'Лёгкая атлетика' }
export const initialAthleteId = 4

export const athletes: Athlete[] = [
  { id: 1, name: 'Мария Иванова', sport: 'Бег', age: 22, trainerId: trainer.id,
    injuries: [{ title: 'Колено', date: '12.09.2026', note: 'Щадящая нагрузка после растяжения.' }],
    nutrition: [{ date: '14.10.2026', title: 'План питания', note: 'Три основных приёма пищи, вода во время тренировки.' }] },
  { id: 2, name: 'Илья Петров', sport: 'Бег', age: 19, trainerId: trainer.id,
    injuries: [], nutrition: [{ date: '13.10.2026', title: 'Дневник питания', note: 'Добавить перекус после тренировки.' }] },
  { id: 3, name: 'Анна Кузнецова', sport: 'ОФП', age: 25, trainerId: trainer.id,
    injuries: [{ title: 'Голеностоп', date: '03.10.2026', note: 'Восстановление; избегать прыжковых упражнений.' }],
    nutrition: [{ date: '12.10.2026', title: 'Рекомендация', note: 'Поддерживать регулярный режим питания.' }] },
  { id: 4, name: 'Мария Соколова', sport: 'Бег', age: 21, trainerId: null,
    injuries: [], nutrition: [] },
]

// Дни недели: 0 — понедельник. Расписание относится к отображаемой демо-неделе.
export const trainings: Training[] = [
  { id: 1, athleteId: 1, day: 0, time: '09:00', title: 'Лёгкий бег', description: 'Разминка 10 минут, бег 30 минут, заминка.', attendance: 'attended' },
  { id: 2, athleteId: 2, day: 0, time: '11:00', title: 'Интервалы', description: 'Шесть отрезков по 400 метров.', attendance: 'attended' },
  { id: 3, athleteId: 3, day: 1, time: '10:30', title: 'Силовая подготовка', description: 'Упражнения без прыжковой нагрузки.', attendance: 'missed' },
  { id: 4, athleteId: 1, day: 2, time: '09:00', title: 'Темповый бег', description: 'Разминка, 20 минут в ровном темпе, заминка.', attendance: 'planned' },
  { id: 5, athleteId: 2, day: 3, time: '11:00', title: 'Восстановление', description: 'Лёгкий бег и растяжка.', attendance: 'planned' },
  { id: 6, athleteId: 3, day: 4, time: '10:30', title: 'ОФП', description: 'Комплекс на корпус и устойчивость.', attendance: 'planned' },
  { id: 7, athleteId: 1, day: 5, time: '09:30', title: 'Длительный бег', description: 'Спокойный темп 45 минут.', attendance: 'planned' },
]
