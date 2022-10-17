from .database import make_query


def main():
    make_query(
        """\
        CREATE TABLE users(
            id INTEGER not null primary key,
            email VARCHAR(50) unique,
            username VARCHAR(50),
            password_hash VARCHAR
        )
        """
    )

    make_query(
        """\
        CREATE TABLE courses(
            id INTEGER not null primary key,
            name VARCHAR,
            course_code VARCHAR unique,
            img VARCHAR
        )
        """
    )

    make_query(
        """\
        CREATE TABLE participants(
            user_id INTEGER not null references users,
            course_id INTEGER not null references courses on delete cascade,
            is_moderator BOOLEAN,
            is_owner BOOLEAN,
            primary key (user_id, course_id)
        )
        """
    )

    make_query(
        """\
        CREATE TABLE tests(
            id INTEGER not null primary key,
            course_id INTEGER references courses on delete cascade,
            name VARCHAR,
            creation_time DATE
        )
        """
    )

    make_query(
        """\
        CREATE TABLE questions(
            id INTEGER not null primary key,
            test_id INTEGER references tests on delete cascade,
            question VARCHAR
        )
        """
    )

    make_query(
        """\
        CREATE TABLE answers(
            id INTEGER not null primary key,
            question_id INTEGER references questions on delete cascade,
            answer VARCHAR,
            is_right BOOLEAN
        )
        """
    )

    make_query(
        """\
        CREATE TABLE users_answers(
            id INTEGER not null primary key,
            user_id INTEGER references users,
            answer_id INTEGER references answers on delete cascade,
            is_selected BOOLEAN
        )
        """
    )

    make_query(
        """\
        CREATE TABLE questions_results(
            id INTEGER not null primary key,
            user_id INTEGER references users,
            question_id INTEGER references questions on delete cascade,
            score FLOAT
        )
        """
    )

    make_query(
        """\
        CREATE TABLE results(
            id INTEGER not null primary key,
            user_id INTEGER references users,
            test_id INTEGER references tests on delete cascade,
            max_score INTEGER,
            score FLOAT
        )
        """
    )


if __name__ == "__main__":
    main()
