import os
import re
import requests
from bs4 import BeautifulSoup, ResultSet
from concurrent.futures import ThreadPoolExecutor, as_completed


class Scrapper:
    def __init__(self) -> None:
        self.url = "https://www.practicepython.org"
        self.response = requests.get(self.url + "/exercises/")
        self.doc = self.response.text
        self.soup = BeautifulSoup(self.doc, "html.parser")
        self.module_dir = os.path.dirname(__file__)
        self.exercises_dir = os.path.join(self.module_dir, "exercises")

        if not os.path.isdir(self.exercises_dir):
            os.mkdir(self.exercises_dir)

    def get_amount_and_exercises(self) -> tuple[int, ResultSet]:
        lis = self.soup.select('li a[href*="/exercise/"]')
        return (len(lis), lis)

    def get_a_soup(self, url: str) -> BeautifulSoup:
        response = requests.get(url)
        doc = response.text
        return BeautifulSoup(doc, "html.parser")

    def write_exercise(self, e, exercise_file_path: str):
        # Create a specific bowl of BeautifulSoup for each exercise href
        soup = self.get_a_soup(self.url + e["href"])
        # Get the exercise contents
        div = soup.find("div", {"class": "boxframe center"})
        # Clean the exercise content from unneeded blank lines ("\n")
        raw_contents = div.text if div else ""
        clean_contents = re.sub(r"\n+", "\n", raw_contents)
        # Write the contents for its respective txt file
        with open(exercise_file_path, "w") as file:
            file.write(clean_contents)

    def get_exercises(self):
        exercises = self.get_amount_and_exercises()[1]
        # Map futures to file paths
        future_to_file = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            for e in exercises:
                exercise_number = str(e["href"]).split("/")[5].split("-")[0]
                exercise_file_path = os.path.join(
                    self.exercises_dir, f"exercise{exercise_number}.txt"
                )
                future = executor.submit(self.write_exercise, e, exercise_file_path)
                future_to_file[future] = exercise_file_path
            for future in as_completed(future_to_file):
                # Use the future-path map to print logs
                file_path = future_to_file[future]
                try:
                    future.result()
                    print(f"{file_path} has been written.")
                except Exception as exc:
                    print(f"{file_path} generated an exception: {exc}")


if __name__ == "__main__":
    scrapper = Scrapper()
    scrapper.get_exercises()
