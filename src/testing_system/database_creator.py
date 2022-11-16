from .database import make_query


def main():
    make_query(
        """\
        create table users (
        id int not null,
        email varchar(50),
        username varchar(50),
        password_hash text,
        primary key (id),
        unique (email)
        )
        """
    )

    make_query(
        """\
        create table courses (
        id int not null,
        name text,
        course_code varchar(10),
        img text,
        primary key (id),
        unique (course_code)
        )
        """
    )

    make_query(
        """\
        create table participants (
        user_id int not null,
        course_id int not null,
        is_moderator boolean,
        is_owner boolean,
        CONSTRAINT fk1 foreign key (user_id) references users(id),
        CONSTRAINT fk2 foreign key (course_id) references courses(id) on delete cascade,
        primary key (user_id, course_id)
        )
        """
    )

    make_query(
        """\
        create table tests (
        id int not null,
        course_id int,
        name text,
        creation_time date,
        primary key (id),
        CONSTRAINT fk3 foreign key (course_id) references courses(id) on delete cascade
        )
        """
    )

    make_query(
        """\
        create table questions (
        id int not null,
        test_id int,
        question text,
        primary key (id),
        CONSTRAINT fk4 foreign key (test_id) references tests(id) on delete cascade
        )
        """
    )

    make_query(
        """\
        create table answers (
        id int not null,
        question_id int,
        answer text,
        is_right boolean,
        primary key (id),
        CONSTRAINT fk5 foreign key (question_id) references questions(id) on delete cascade
        )
        """
    )

    make_query(
        """\
        create table users_answers (
        id int not null,
        user_id int,
        answer_id int,
        is_selected boolean,
        primary key (id),
        CONSTRAINT fk6 foreign key (user_id) references users(id),
        CONSTRAINT fk7 foreign key (answer_id) references answers(id) on delete cascade
        )
        """
    )

    make_query(
        """\
        create table questions_results (
        id int not null,
        user_id int,
        question_id int,
        score float,
        primary key (id),
        CONSTRAINT fk8 foreign key (user_id) references users(id),
        CONSTRAINT fk9 foreign key (question_id) references questions(id) on delete cascade
        )
        """
    )

    make_query(
        """\
        create table results (
        id int not null,
        user_id int,
        test_id int,
        max_score int,
        score float,
        primary key (id),
        CONSTRAINT fk10 foreign key (user_id) references users(id),
        CONSTRAINT fk11 foreign key (test_id) references tests(id) on delete cascade
        )
        """
    )

    make_query(
        """\
        CREATE TRIGGER before_course_update BEFORE UPDATE on courses
        FOR EACH ROW
        BEGIN
           IF NEW.id != OLD.id THEN
               SET NEW='id cannot be changed';
           END IF;
        END;
        """
    )


if __name__ == "__main__":
    main()
