#ifndef DUNE_POLYGONGRID_GRID_HH
#define DUNE_POLYGONGRID_GRID_HH

#include <memory>
#include <utility>

#include <dune/geometry/dimension.hh>

#include <dune/grid/common/grid.hh>

#include <dune/polygongrid/capabilities.hh>
#include <dune/polygongrid/gridfamily.hh>

namespace Dune
{

  // PolygonGrid
  // -----------

  template< class ct >
  class PolygonGrid
    : public Dune::GridDefaultImplementation< 2, 2, ct, __PolygonGrid::GridFamily< ct > >
  {
    typedef PolygonGrid< ct > This;
    typedef Dune::GridDefaultImplementation< 2, 2, ct, __PolygonGrid::GridFamily< ct > > Base;

    friend class __PolygonGrid::IdSet< ct >;
    friend class __PolygonGrid::IndexSet< ct >;
    friend class __PolygonGrid::GridView< ct >;

  public:
    typedef __PolygonGrid::GridFamily< ct > GridFamily;

    typedef typename GridFamily::Traits Traits;

    static const int dimension = 2;
    static const int dimensionworld = 2;

    typedef typename Traits::MacroGridView MacroGridView;

    typedef typename Base::LeafGridView LeafGridView;
    typedef typename Base::LevelGridView LevelGridView;

    typedef typename Base::GlobalIdSet GlobalIdSet;
    typedef typename Base::LocalIdSet LocalIdSet;

    typedef typename Base::LeafIndexSet LeafIndexSet;
    typedef typename Base::LevelIndexSet LevelIndexSet;

    typedef typename Base::Communication Communication;
    typedef Communication CollectiveCommunication;

    typedef __PolygonGrid::Mesh< ct > Mesh;
    typedef __PolygonGrid::MeshType MeshType;

    PolygonGrid ( std::shared_ptr< Mesh > mesh, __PolygonGrid::MeshType type )
      : mesh_( std::move( mesh ) ), type_( std::move( type ) ),
        indexSet_( *mesh_, type_ )
    {}

    PolygonGrid ( const This &other )
      : mesh_( other.mesh_ ), type_( other.type_ ),
        indexSet_( *mesh_, type_ )
    {}

    PolygonGrid ( This &other )
      : mesh_( std::move( other.mesh_ ) ), type_( std::move( other.type_ ) ),
        indexSet_( *mesh_, type_ )
    {}

    int maxLevel () const { return 0; }

    std::size_t numBoundarySegments () const { return mesh().numBoundaries( type() ); }

    MacroGridView macroGridView () const { return __PolygonGrid::GridView< ct > ( *this ); }

    LevelGridView levelGridView ( int level ) const { assert( level == 0 ); return macroGridView(); }
    LeafGridView leafGridView () const { return macroGridView(); }

    const GlobalIdSet &globalIdSet () const { return idSet_; }
    const LocalIdSet &localIdSet () const { return idSet_; }

    bool globalRefine ( int refCount ) { return false; }

    bool mark ( int refCount, const typename Traits::template Codim< 0 >::Entity &entity ) const { return false; }
    int getMark ( const typename Traits::template Codim< 0 >::Entity &entity ) const { return 0; }

    bool preAdapt () { return false; }
    bool adapt () { return false; }
    void postAdapt () {}

    const Communication &comm () const { return comm_; }

    bool loadBalance () { return false; }

    template< class DataHandle >
    bool loadBalance ( DataHandle &data )
    {
      return false;
    }

    template< class Seed >
    typename Traits::template Codim< Seed::codimension >::Entity entity ( const Seed &seed ) const noexcept
    {
      typedef __PolygonGrid::Entity< Seed::codimension, 2, const This > EntityImpl;
      typedef typename std::conditional< Seed::codimension == 1, __PolygonGrid::HalfEdge< ct >, __PolygonGrid::Node< ct > >::type Item;
      return EntityImpl( Item( mesh_.get(), seed.impl().index() ) );
    }

    // deprecated interface methods

    int size ( int codim ) const { return leafGridView().size( codim ); }
    int size ( GeometryType type ) const { return leafGridView().size( type ); }
    int size ( int level, int codim ) const { return levelGridView( level ).size( codim ); }
    int size ( int level, GeometryType type ) const { return levelGridView( level ).size( type ); }

    int ghostSize( int ) const { return 0; }
    int overlapSize( int ) const { return 0; }

    const LeafIndexSet &leafIndexSet () const { return indexSet_; }
    const LevelIndexSet &levelIndexSet ( int level ) const { assert( level == 0 ); return indexSet_; }

    // non-interface methods

    This dualGrid () const { return This( mesh_, dual( type() ) ); }

    const Mesh &mesh () const { return *mesh_; }
    MeshType type () const { return type_; }

  private:
    std::shared_ptr< Mesh > mesh_;
    __PolygonGrid::MeshType type_;
    Communication comm_;
    LocalIdSet idSet_;
    __PolygonGrid::IndexSet< ct > indexSet_;
  };

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_GRID_HH
