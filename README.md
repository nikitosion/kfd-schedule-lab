# «Ничего не падает» — работа с расписанием

Реализуйте консольное приложение на Kotlin: оно читает расписание, выбирает занятия по дате или типу и сообщает об ошибках во входных данных. Опишите занятия и результаты разбора типами, которые не допускают некорректных состояний.

- [Условия задания](docs/assignment.md): модель, формат данных, команды и сообщения об ошибках.
- [Памятка по реализации](docs/student-guide.md): чтение файла, неизменяемые коллекции и тесты.

## Начало работы

1. Сделайте Fork репозитория и клонируйте свою копию на компьютер.
2. Установите **JDK 25** и **Python 3.10+**. Укажите путь к JDK в `JAVA_HOME` и выберите JDK 25 для Gradle в IDE.
3. Прочитайте условия и посмотрите файлы в `samples/`.
4. Замените заглушку в `app/src/main/kotlin/schedule/Main.kt` своей реализацией. Размещайте код в `app/src/main/kotlin`, тесты — в `app/src/test/kotlin`.

В проекте используются Kotlin **2.4.10**, Gradle **9.5.1** и JUnit **6.1.3**. Kotlin и Gradle отдельно устанавливать не нужно: используйте Gradle Wrapper. При первой сборке понадобится интернет для загрузки зависимостей.

## Сборка и команды

Выполняйте команды из корня проекта. На Windows вместо `python` можно использовать `py -3`.

Windows PowerShell:

```powershell
.\gradlew.bat build :app:installDist
.\app\build\install\schedule\bin\schedule.bat period --file samples/clean.txt --from 2026-09-28 --to 2027-05-13
.\app\build\install\schedule\bin\schedule.bat type --file samples/dirty.txt --type СДАЧА
.\app\build\install\schedule\bin\schedule.bat errors --file samples/dirty.txt
```

Linux/macOS:

```bash
bash ./gradlew build :app:installDist
./app/build/install/schedule/bin/schedule period --file samples/clean.txt --from 2026-09-28 --to 2027-05-13
./app/build/install/schedule/bin/schedule type --file samples/dirty.txt --type СДАЧА
./app/build/install/schedule/bin/schedule errors --file samples/dirty.txt
```

`build` компилирует приложение и выполняет тесты, `installDist` создаёт исполняемые скрипты. Команды расписания нужно реализовать в задании.

Большой входной файл создаётся командой `python tools/generate_samples.py --huge` (на Linux/macOS — `python3`). Файл `samples/huge.txt` исключён из Git.

После реализации можно сравнить вывод с эталонами командой `python tools/verify.py` (на Linux/macOS — `python3`). Для неё нужны установленное через `installDist` приложение и `samples/huge.txt`.

Отправьте ссылку на репозиторий с решением в Academy. Срок указан в задании.
