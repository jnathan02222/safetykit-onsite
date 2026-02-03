# Atlas

> I can't get that melody out of my head
>
> Music connects worlds that should not be linked

<img width="3024" height="1712" alt="image" src="https://github.com/user-attachments/assets/7359c8ee-bbe8-48ff-8561-c71472a2dd86" />

Atlas is an interactive graph of musicians. Artists that are related
are linked together, whether they inspired one another,
played at the same concert or made a song together. You can look
up a musician to see correlated artists, then click on those
nodes to find more artists and explore the space!

The idea is that the data that determines these connections will
be aggregated from various sources or "integrations" (inspired by my
work at [Secoda](https://www.secoda.co/)), though currently the primary
integration is Wikipedia (I've been reading a lot on Wikipedia).

Why [your-song-connects-worlds.com](https://your-song-connects-worlds.com/)?
It's a reference to something that inspired this project :)

## Backend

A [Django Ninja](https://django-ninja.dev/) API that let's you search
musicians and their relationships.

Also contains scraping scripts, with plans to use Celery in the future to make
this a recurring job.

See the `README.md` in `/api` for more details.

## Frontend

A [Next](https://nextjs.org/) (hey it's easy to deploy) app that provides
the interactive UI for searching.

See the `README.md` in `/frontend` for more details.

## Testing

Since this is a personal project tests are currently a low priority, but I will look
into adding tests with [Pytest](https://docs.pytest.org/en/stable/) and
[Playwright](https://playwright.dev/) in the future.

## Deployment

Frontend deployment is automatically managed by Vercel (again, it's easy).

The backend is organized into various Docker containers. See more in the `README.md`
for `/deploy`.

## Contributing

The main ways to contribute to this project are to add integrations, or, if you're feeling
ambitious, implementing a cool graph algorithm to use (for instance shortest path).
