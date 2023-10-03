@app.route('/api.backup_tracker', methods = ['POST'])
def tasks():

    if 'task_id' not in request.form:
        with psycopg2.connect(db_uri) as conn, conn.cursor() as cur:
            try:
                cur.execute(
                    '''
                        INSERT INTO tasks (
                            job_id, 
                            starttime, 
                            status_id, 
                            log_url
                        ) 
                        VALUES (
                            (
                                SELECT job_id
                                FROM jobs_master
                                WHERE 
                                    scope = %(scope)s AND
                                    backup_software = %(backup_software)s AND
                                    source_storage = %(source_storage)s AND
                                    destination_storage = %(destination_storage)s AND
                                    level = %(level)s  
                            ),
                            localtimestamp(0),
                            (SELECT status_id FROM status WHERE status = %(status)s),
                            %(log)s
                        )
                        RETURNING task_id;
                    ''', 
                    request.form
                )
            except BaseException as be:
                return (be, 400)
            else:
                return str( cur.fetchone()[0] )

    else:
        with psycopg2.connect(db_uri) as conn, conn.cursor() as cur:
            try:
                cur.execute(
                    '''
                        UPDATE 
                            tasks
                        SET 
                            status_id = (SELECT status_id FROM status WHERE status = %s),
                            gib = round(%s, 2),
                            endtime = localtimestamp(0)
                        WHERE 
                            task_id = %s
                    ''',
                    [ request.form[task_field] for task_field in ['status', 'gib', 'task_id'] ]
                )
            except BaseException as be:
                return (be, 400)
            else:
                return ('', 204)
