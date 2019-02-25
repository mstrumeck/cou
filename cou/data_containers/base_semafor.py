from abc import ABC

from cou.global_var import ELEMENTARY, COLLEGE, PHD


class BaseSemafor(ABC):
    def _create_data_for_building_with_worker(
        self, data_container, citizens, citizens_in_city
    ):
        data_container.workers_costs = 0
        data_container.max_employees = sum(
            [
                data_container.bi.elementary_employee_needed,
                data_container.bi.college_employee_needed,
                data_container.bi.phd_employee_needed,
            ]
        )

        data_container.elementary_employees = [
            e
            for e in citizens
            if e.workplace_object == data_container.bi
            and citizens_in_city[e].current_profession.education in (ELEMENTARY, "None")
        ]

        data_container.elementary_vacancies = data_container.bi.elementary_employee_needed - len(
            [
                e
                for e in citizens
                if e.workplace_object == data_container.bi
                and citizens_in_city[e].current_profession.education == ELEMENTARY
            ]
        )

        data_container.college_employees = [
            e
            for e in citizens
            if e.workplace_object == data_container.bi
            and citizens_in_city[e].current_profession.education == COLLEGE
        ]

        data_container.college_vacancies = data_container.bi.college_employee_needed - len(
            [
                e
                for e in citizens
                if e.workplace_object == data_container.bi
                and citizens_in_city[e].current_profession.education == COLLEGE
            ]
        )

        data_container.phd_employees = [
            e
            for e in citizens
            if e.workplace_object == data_container.bi
            and citizens_in_city[e].current_profession.education == PHD
        ]

        data_container.phd_vacancies = data_container.bi.phd_employee_needed - len(
            [
                e
                for e in citizens
                if e.workplace_object == data_container.bi
                and citizens_in_city[e].current_profession.education == PHD
            ]
        )

        data_container.all_employees = (
                data_container.elementary_employees + data_container.college_employees + data_container.phd_employees
        )
        data_container.people_in_charge = len(data_container.all_employees)
