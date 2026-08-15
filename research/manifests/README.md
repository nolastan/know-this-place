# Manifests

Parcel lists produced by research, consumed by the website's seeder:

```bash
python3 scripts/seed_pages.py seed-list --manifest research/manifests/<file>.json
```

A manifest is what a [publisher](../roles/publisher.md) writes when a source
names a lot of buildings that have no pages yet — an inventory in a context
statement, a survey's list of contributors to a district. The seeder joins the
city datasets onto the parcels named here and writes each page's first draft;
the facts *from the source* are then hand-added to those pages, because the
seeder never invents prose and knows nothing about the source.

- One manifest per source or survey, named after it.
- Entry shape: see any existing file, and the `seed-list` docstring in
  `scripts/seed_pages.py`. The parcel is stated outright (`apn`), because
  downtown EAS rows often carry retired APNs that the address→parcel join
  silently drops.
- Manifests are create-only inputs: re-running `seed-list` writes nothing for a
  page that already exists.

Keeping them here rather than under `scripts/` is the module boundary — the
list of parcels is a research finding; the script that reads it is site tooling.
