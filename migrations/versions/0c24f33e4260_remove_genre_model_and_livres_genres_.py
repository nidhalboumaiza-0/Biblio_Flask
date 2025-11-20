from alembic import op
import sqlalchemy as sa

# Add these lines
revision = '0c24f33e4260'  # Replace with the revision ID from the filename
down_revision = 'cccdbb475abc'  # Replace with the previous migration's revision ID

def upgrade():
    # Drop the foreign key constraint in the livres_genres table
    op.drop_constraint('livres_genres_ibfk_2', 'livres_genres', type_='foreignkey')
    
    # Drop the livres_genres association table
    op.drop_table('livres_genres')
    
    # Drop the genres table
    op.drop_table('genres')

def downgrade():
    # Recreate the genres table
    op.create_table(
        'genres',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nom', sa.String(50), nullable=False, unique=True)
    )
    
    # Recreate the livres_genres association table
    op.create_table(
        'livres_genres',
        sa.Column('livre_id', sa.Integer, sa.ForeignKey('livres.id'), primary_key=True),
        sa.Column('genre_id', sa.Integer, sa.ForeignKey('genres.id'), primary_key=True)
    )